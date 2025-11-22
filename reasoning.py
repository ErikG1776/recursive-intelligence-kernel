"""
reasoning.py  |  Recursive Intelligence Algorithm (RIA) v5.0
Bricks 2-5: Grammar Validation + Abstraction Creation + Analogy Validation
---------------------------------------------------------------------------
Provides:
1. TASK_GRAMMAR schema validation
2. Abstraction discovery via DBSCAN clustering
3. Analogy validation using graph isomorphism + TF-IDF semantic similarity
"""

import json
from datetime import datetime
from typing import Optional
from functools import lru_cache
import numpy as np
from jsonschema import validate, ValidationError
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx

from config import setup_logging, DBSCAN_EPS, DBSCAN_MIN_SAMPLES, TFIDF_SIM_THRESHOLD
from db import get_cursor, execute_many

logger = setup_logging("rik.reasoning")


# ==========================================================
# === Brick 2 : Full Task Grammar Schema ===================
# ==========================================================
TASK_GRAMMAR = {
    "type": "object",
    "required": ["nodes", "edges"],
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "primitive"],
                "properties": {
                    "id": {"type": "string"},
                    "primitive": {"enum": ["locate", "transform", "validate", "execute"]},
                    "params": {"type": "object"},
                    "timeout": {"type": "number", "default": 30},
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to"],
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "condition": {"type": "string", "default": "always"},
                },
            },
        },
    },
}


def validate_task_schema(task: dict) -> bool:
    """Validate a task dict against TASK_GRAMMAR."""
    try:
        validate(instance=task, schema=TASK_GRAMMAR)
        logger.info("Task validated successfully against grammar")
        return True
    except ValidationError as e:
        logger.warning(f"Task validation failed: {e.message}")
        return False


# ==========================================================
# === Brick 4 : Abstraction Creation =======================
# ==========================================================

def extract_sequences() -> list[str]:
    """Retrieve prior task sequences (primitive patterns) from episodes table."""
    with get_cursor(commit=False) as cursor:
        cursor.execute("SELECT task FROM episodes WHERE task IS NOT NULL")
        rows = cursor.fetchall()
    return [r[0] for r in rows if r[0]]


# Cache vectorizer to avoid recomputation
_vectorizer_cache: dict[str, TfidfVectorizer] = {}


def get_cached_vectorizer(cache_key: str = "default") -> TfidfVectorizer:
    """Get or create a cached TF-IDF vectorizer."""
    if cache_key not in _vectorizer_cache:
        _vectorizer_cache[cache_key] = TfidfVectorizer(stop_words="english")
    return _vectorizer_cache[cache_key]


def create_abstractions(sim_threshold: float = TFIDF_SIM_THRESHOLD) -> list[dict]:
    """
    Cluster similar primitive sequences and register new abstractions.

    Returns:
        List of created abstractions.
    """
    sequences = extract_sequences()
    if not sequences:
        logger.info("No sequences found - add episodes first")
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sequences)

    clustering = DBSCAN(
        eps=DBSCAN_EPS,
        min_samples=DBSCAN_MIN_SAMPLES,
        metric="cosine"
    ).fit(X)
    labels = clustering.labels_

    cluster_map: dict[int, list[str]] = {}
    for label, seq in zip(labels, sequences):
        if label == -1:
            continue
        cluster_map.setdefault(label, []).append(seq)

    new_abstractions = []
    for label, seqs in cluster_map.items():
        if len(seqs) >= 2:
            joined = " | ".join(seqs)
            abstraction_name = f"abstract_{label}"
            new_abstractions.append({
                "name": abstraction_name,
                "definition": joined
            })
            logger.info(f"Created abstraction: {abstraction_name}")

    # Batch persist abstractions
    if new_abstractions:
        with get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abstractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    definition TEXT,
                    timestamp TEXT
                )
            """)

            timestamp = datetime.utcnow().isoformat()
            params = [
                (abs_["name"], abs_["definition"], timestamp)
                for abs_ in new_abstractions
            ]
            cursor.executemany(
                "INSERT INTO abstractions (name, definition, timestamp) VALUES (?, ?, ?)",
                params
            )

        logger.info(f"{len(new_abstractions)} new abstractions saved")
    else:
        logger.info("No new abstractions discovered this round")

    return new_abstractions


# ==========================================================
# === Brick 5 : Analogy Validation =========================
# ==========================================================

def build_graph(task: dict) -> nx.DiGraph:
    """Convert a task dict (nodes/edges) into a NetworkX DiGraph."""
    G = nx.DiGraph()
    for node in task.get("nodes", []):
        G.add_node(
            node["id"],
            primitive=node.get("primitive", ""),
            params=node.get("params", {})
        )
    for edge in task.get("edges", []):
        G.add_edge(
            edge["from"],
            edge["to"],
            condition=edge.get("condition", "always")
        )
    return G


def compute_tfidf_similarity(texts_a: list[str], texts_b: list[str]) -> float:
    """
    Compute average TF-IDF similarity between two text sets.
    Uses cached vectorizer for better performance.
    """
    if not texts_a or not texts_b:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    all_texts = texts_a + texts_b
    X = vectorizer.fit_transform(all_texts)

    n = len(texts_a)
    sim_matrix = (X * X.T).toarray()
    cross = sim_matrix[:n, n:]
    return float(np.mean(cross))


def avg_tfidf_similarity(a_nodes: list[dict], b_nodes: list[dict]) -> float:
    """Compute average TF-IDF similarity between two node sets."""
    texts_a = [
        " ".join([n.get("primitive", "")] + list(map(str, n.get("params", {}).values())))
        for n in a_nodes
    ]
    texts_b = [
        " ".join([n.get("primitive", "")] + list(map(str, n.get("params", {}).values())))
        for n in b_nodes
    ]
    return compute_tfidf_similarity(texts_a, texts_b)


def validate_analogy(
    task_a: dict,
    task_b: dict,
    sim_threshold: float = TFIDF_SIM_THRESHOLD
) -> bool:
    """
    Return True if tasks are analogous both structurally (isomorphism)
    and semantically (TF-IDF >= threshold).
    """
    G1, G2 = build_graph(task_a), build_graph(task_b)

    iso = nx.is_isomorphic(
        G1, G2,
        node_match=lambda x, y: x["primitive"] == y["primitive"]
    )
    if not iso:
        logger.info("Graphs are not structurally analogous")
        return False

    sem_sim = avg_tfidf_similarity(task_a["nodes"], task_b["nodes"])
    if sem_sim >= sim_threshold:
        logger.info(f"Tasks are analogous (TF-IDF similarity = {sem_sim:.2f})")
        return True
    else:
        logger.warning(f"Structural match but low semantic similarity ({sem_sim:.2f})")
        return False


# ==========================================================
# === Manual Test Runner ===================================
# ==========================================================
if __name__ == "__main__":
    # Grammar validation
    sample_task = {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"selector": "#input"}},
            {"id": "2", "primitive": "execute", "params": {"action": "click"}},
        ],
        "edges": [{"from": "1", "to": "2"}],
    }
    validate_task_schema(sample_task)

    # Abstraction creation
    create_abstractions()

    # Analogy validation demo
    task1 = {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"selector": "#input"}},
            {"id": "2", "primitive": "execute", "params": {"action": "click"}},
        ],
        "edges": [{"from": "1", "to": "2"}],
    }
    task2 = {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"selector": "#button"}},
            {"id": "2", "primitive": "execute", "params": {"action": "press"}},
        ],
        "edges": [{"from": "1", "to": "2"}],
    }
    validate_analogy(task1, task2)

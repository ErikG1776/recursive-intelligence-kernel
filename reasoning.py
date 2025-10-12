"""
reasoning.py  |  Recursive Intelligence Kernel (RIK) v5.0
Bricks 2–5: Grammar Validation + Abstraction Creation + Analogy Validation
---------------------------------------------------------------------------
Provides:
1. TASK_GRAMMAR schema validation
2. Abstraction discovery via DBSCAN clustering
3. Analogy validation using graph isomorphism + TF-IDF semantic similarity
"""

import os, json, sqlite3
from datetime import datetime
import numpy as np
from jsonschema import validate, ValidationError
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx


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
        print("[✅] Task validated successfully against grammar.")
        return True
    except ValidationError as e:
        print(f"[❌] Task validation failed: {e.message}")
        return False


# ==========================================================
# === Brick 4 : Abstraction Creation ========================
# ==========================================================
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "memory.db")


def extract_sequences():
    """Retrieve prior task sequences (primitive patterns) from episodes table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT description FROM episodes")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def create_abstractions(sim_threshold: float = 0.7):
    """Cluster similar primitive sequences and register new abstractions."""
    sequences = extract_sequences()
    if not sequences:
        print("[ℹ️] No sequences found — add episodes first.")
        return

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sequences)

    clustering = DBSCAN(eps=0.7, min_samples=2, metric="cosine").fit(X)
    labels = clustering.labels_

    cluster_map = {}
    for label, seq in zip(labels, sequences):
        if label == -1:
            continue
        cluster_map.setdefault(label, []).append(seq)

    new_abstractions = []
    for label, seqs in cluster_map.items():
        joined = " | ".join(seqs)
        if len(seqs) >= 2:
            abstraction_name = f"abstract_{label}"
            new_abstractions.append({"name": abstraction_name, "definition": joined})
            print(f"[🧩] Created abstraction → {abstraction_name}")

    # Persist abstractions
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS abstractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            definition TEXT,
            timestamp TEXT
        )
    """)
    for abs_ in new_abstractions:
        c.execute(
            "INSERT INTO abstractions (name, definition, timestamp) VALUES (?, ?, ?)",
            (abs_["name"], abs_["definition"], datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()

    if new_abstractions:
        print(f"[✅] {len(new_abstractions)} new abstractions saved.")
    else:
        print("[ℹ️] No new abstractions discovered this round.")


# ==========================================================
# === Brick 5 : Analogy Validation ==========================
# ==========================================================
def build_graph(task: dict):
    """Convert a task dict (nodes/edges) into a NetworkX DiGraph."""
    G = nx.DiGraph()
    for node in task.get("nodes", []):
        G.add_node(node["id"], primitive=node.get("primitive", ""), params=node.get("params", {}))
    for edge in task.get("edges", []):
        G.add_edge(edge["from"], edge["to"], condition=edge.get("condition", "always"))
    return G


def avg_tfidf_similarity(a_nodes, b_nodes):
    """Compute average TF-IDF similarity between two node sets."""
    texts_a = [" ".join([n.get("primitive", "")] + list(map(str, n.get("params", {}).values()))) for n in a_nodes]
    texts_b = [" ".join([n.get("primitive", "")] + list(map(str, n.get("params", {}).values()))) for n in b_nodes]
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts_a + texts_b)
    n = len(texts_a)
    sim_matrix = (X * X.T).toarray()
    cross = sim_matrix[:n, n:]
    return float(np.mean(cross))


def validate_analogy(task_a: dict, task_b: dict, sim_threshold: float = 0.7) -> bool:
    """
    Return True if tasks are analogous both structurally (isomorphism)
    and semantically (TF-IDF ≥ threshold).
    """
    G1, G2 = build_graph(task_a), build_graph(task_b)

    iso = nx.is_isomorphic(G1, G2, node_match=lambda x, y: x["primitive"] == y["primitive"])
    if not iso:
        print("[❌] Graphs are not structurally analogous.")
        return False

    sem_sim = avg_tfidf_similarity(task_a["nodes"], task_b["nodes"])
    if sem_sim >= sim_threshold:
        print(f"[✅] Tasks are analogous (TF-IDF similarity = {sem_sim:.2f}).")
        return True
    else:
        print(f"[⚠️] Structural match found but low semantic similarity ({sem_sim:.2f}).")
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

    # Abstraction creation (will show "no sequences" on first run)
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
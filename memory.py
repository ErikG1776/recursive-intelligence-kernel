"""
memory.py  |  Recursive Intelligence Kernel (RIK) v5.0
Brick 3: DBSCAN Consolidation
--------------------------------------------
Clusters related episodes and prunes unused memory
to maintain bounded rationality.
"""

import os
import sqlite3
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "memory.db")

# Ensure episodes table exists
def _init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            utility REAL,
            dependency_links TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

_init_db()


def save_episode(description: str, utility: float = 1.0, dependency_links=None):
    """Store a new experience tuple in the database."""
    if dependency_links is None:
        dependency_links = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO episodes (description, utility, dependency_links, timestamp)
        VALUES (?, ?, ?, ?)
    """, (description, utility, ",".join(map(str, dependency_links)), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    print(f"[💾] Episode saved: {description[:50]}...")


def consolidate_episodes(eps: float = 0.15, min_samples: int = 2):
    """
    Consolidates semantically similar episodes using TF-IDF + DBSCAN.
    Prunes low-utility episodes with no dependency links.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, description, utility, dependency_links FROM episodes")
    rows = c.fetchall()

    if not rows:
        print("[ℹ️] No episodes to consolidate yet.")
        conn.close()
        return

    ids = [r[0] for r in rows]
    texts = [r[1] for r in rows]
    utilities = [r[2] for r in rows]
    dependencies = [r[3] for r in rows]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)

    # DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    labels = clustering.labels_

    # Consolidate clusters
    cluster_summary = {}
    for label, id_, desc, util in zip(labels, ids, texts, utilities):
        if label == -1:
            continue  # noise
        if label not in cluster_summary:
            cluster_summary[label] = {"count": 0, "text": [], "utility": []}
        cluster_summary[label]["count"] += 1
        cluster_summary[label]["text"].append(desc)
        cluster_summary[label]["utility"].append(util)

    # Create summary entries
    for label, info in cluster_summary.items():
        combined = " ".join(info["text"])
        avg_util = sum(info["utility"]) / len(info["utility"])
        save_episode(f"[Cluster {label}] {combined[:100]}", avg_util)

    # Prune low-utility episodes with no dependencies
    low_util_threshold = 0.3
    pruned = 0
    for (id_, desc, util, deps) in rows:
        if util < low_util_threshold and not deps:
            c.execute("DELETE FROM episodes WHERE id = ?", (id_,))
            pruned += 1

    conn.commit()
    conn.close()
    print(f"[✅] Consolidation complete. Clusters: {len(cluster_summary)} | Pruned: {pruned}")
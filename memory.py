"""
memory.py | Recursive Intelligence Kernel (RIK)
--------------------------------------------------------------------
Manages multi-type memory persistence for the Recursive Intelligence Kernel.
Handles episodic storage, semantic mappings, and dependency-aware consolidation.
"""

import sqlite3
import json
import os
from datetime import datetime
from exceptions import MemoryException, DatabaseException, ConsolidationException


# ==========================================================
# 🔧  CENTRALIZED DATABASE PATH
# ==========================================================

def get_db_path():
    """
    Returns the absolute path to the memory database.
    Ensures consistent path resolution across all modules.
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "memory.db")


# ==========================================================
# 🧠  INITIALIZATION
# ==========================================================

def init_memory_db():
    """
    Initialize the SQLite memory database with required tables if missing.
    Creates both general episodes and fallback-specific episodic_memory tables.
    """
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # General task episodes
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            result TEXT,
            reflection TEXT
        )
        """
    )

    # Fallback/recovery episodes for learning
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            error_type TEXT,
            strategy TEXT,
            predicted_success REAL,
            actual_outcome TEXT,
            context TEXT
        )
        """
    )

    # Code modifications tracking
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            component TEXT,
            change_description TEXT,
            performance_before REAL,
            performance_after REAL,
            rollback_code TEXT
        )
        """
    )

    # Strategy learning weights
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT UNIQUE,
            success_rate REAL,
            avg_confidence REAL,
            last_updated TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ==========================================================
# 💾  EPISODIC MEMORY
# ==========================================================

def save_episode(task: str, result: str, reflection: str):
    """
    Save a new episodic memory entry to the database.
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO episodes (timestamp, task, result, reflection) VALUES (?, ?, ?, ?)",
        (timestamp, task, result, reflection),
    )
    conn.commit()
    conn.close()
    print(f"[MEMORY] Episode saved at {timestamp}")


def get_recent_episodes(limit: int = 5):
    """
    Return the most recent episodic memory entries from the database.

    Args:
        limit: Maximum number of episodes to retrieve

    Returns:
        List of episode dictionaries

    Raises:
        DatabaseException: If database query fails
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        episodes = []
        for row in rows:
            episodes.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "task": row[2],
                    "result": row[3],
                    "reflection": row[4],
                }
            )
        return episodes
    except sqlite3.Error as e:
        print(f"[MEMORY-ERROR] {e}")
        raise DatabaseException(f"Failed to retrieve episodes: {e}")
    finally:
        conn.close()


# ==========================================================
# 🧩  CONSOLIDATION AND PRUNING
# ==========================================================

def consolidate_episodes(eps: float = 0.5, min_samples: int = 2):
    """
    Groups similar episodes into higher-level abstractions using DBSCAN clustering.

    Args:
        eps: Maximum distance between two samples for them to be in same cluster (default: 0.5)
        min_samples: Minimum number of samples in a cluster (default: 2)

    Returns:
        Dictionary with consolidation results including clusters formed
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    import numpy as np

    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    try:
        # Retrieve all episodes
        c.execute("SELECT id, task, result, reflection FROM episodes")
        rows = c.fetchall()

        if not rows or len(rows) < min_samples:
            print(f"[MEMORY] Not enough episodes for clustering (need at least {min_samples})")
            return {"consolidated": False, "reason": "insufficient_data", "clusters": []}

        # Combine task and reflection for clustering
        episode_ids = [row[0] for row in rows]
        episode_texts = [f"{row[1]} {row[3]}" for row in rows]

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf_matrix = vectorizer.fit_transform(episode_texts)

        # Apply DBSCAN clustering
        # Note: DBSCAN uses distance, so we convert similarity to distance (1 - similarity)
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        labels = clustering.fit_predict(tfidf_matrix.toarray())

        # Group episodes by cluster
        clusters = {}
        noise_count = 0

        for idx, label in enumerate(labels):
            if label == -1:  # Noise point
                noise_count += 1
                continue

            if label not in clusters:
                clusters[label] = []

            clusters[label].append({
                "id": episode_ids[idx],
                "task": rows[idx][1],
                "result": rows[idx][2],
                "reflection": rows[idx][3]
            })

        # Create consolidated memories from clusters
        consolidated_count = 0
        for cluster_id, episodes in clusters.items():
            if len(episodes) >= min_samples:
                # Create a consolidated memory entry
                consolidated_task = f"Cluster {cluster_id}: {len(episodes)} similar episodes"
                consolidated_reflection = f"Consolidated learning from {len(episodes)} episodes: " + \
                                        " | ".join([ep["reflection"][:50] for ep in episodes[:3]])

                # Store consolidated memory
                c.execute(
                    "INSERT INTO episodes (timestamp, task, result, reflection) VALUES (?, ?, ?, ?)",
                    (datetime.utcnow().isoformat(), consolidated_task, "consolidated", consolidated_reflection)
                )
                consolidated_count += 1

        conn.commit()

        print(f"[MEMORY] Consolidation complete:")
        print(f"  - Total episodes: {len(rows)}")
        print(f"  - Clusters formed: {len(clusters)}")
        print(f"  - Consolidated memories created: {consolidated_count}")
        print(f"  - Noise points (unclustered): {noise_count}")

        return {
            "consolidated": True,
            "total_episodes": len(rows),
            "clusters_formed": len(clusters),
            "consolidated_memories": consolidated_count,
            "noise_points": noise_count,
            "clusters": clusters
        }

    except Exception as e:
        print(f"[MEMORY-ERROR] Consolidation failed: {e}")
        return {"consolidated": False, "error": str(e)}
    finally:
        conn.close()


# ==========================================================
# 🧠  MEMORY RETRIEVAL / UTILITY
# ==========================================================

def retrieve_context(task: str, top_k: int = 3):
    """
    Retrieve memory context similar to the provided task using TF-IDF semantic search.

    Args:
        task: The task description to search for similar episodes
        top_k: Number of most similar episodes to return (default: 3)

    Returns:
        Dictionary with similar episodes ranked by relevance
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        # Retrieve all episodes with their tasks and reflections
        c.execute("SELECT id, task, result, reflection FROM episodes")
        rows = c.fetchall()

        if not rows or len(rows) == 0:
            return {"context": None, "similar_episodes": []}

        # Extract task descriptions for similarity comparison
        episode_ids = [row[0] for row in rows]
        episode_texts = [f"{row[1]} {row[3]}" for row in rows]  # Combine task + reflection

        # If only one episode exists, return it
        if len(episode_texts) == 1:
            return {
                "context": rows[0][3],
                "similar_episodes": [{
                    "id": rows[0][0],
                    "task": rows[0][1],
                    "result": rows[0][2],
                    "reflection": rows[0][3],
                    "similarity": 1.0
                }]
            }

        # Compute TF-IDF similarity
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        all_texts = episode_texts + [task]
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Calculate cosine similarity between query and all episodes
        query_vector = tfidf_matrix[-1]
        episode_vectors = tfidf_matrix[:-1]
        similarities = cosine_similarity(query_vector, episode_vectors).flatten()

        # Get top-k most similar episodes
        top_indices = np.argsort(similarities)[::-1][:top_k]

        similar_episodes = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include episodes with non-zero similarity
                similar_episodes.append({
                    "id": episode_ids[idx],
                    "task": rows[idx][1],
                    "result": rows[idx][2],
                    "reflection": rows[idx][3],
                    "similarity": round(float(similarities[idx]), 3)
                })

        # Return most relevant reflection as primary context
        primary_context = similar_episodes[0]["reflection"] if similar_episodes else None

        return {
            "context": primary_context,
            "similar_episodes": similar_episodes
        }

    except Exception as e:
        return {"error": str(e), "context": None}
    finally:
        conn.close()


# ==========================================================
# 🧪  SELF-TEST
# ==========================================================

if __name__ == "__main__":
    init_memory_db()
    save_episode("System boot test", "success", "RIK initialized correctly.")
    print(get_recent_episodes())
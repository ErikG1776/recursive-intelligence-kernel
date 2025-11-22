"""
semantic_task_decomposer.py | RIK v5.0
------------------------------------------------------------
Embeds tasks semantically for organic clustering.
No fixed domains - abstractions emerge from embedding similarity.
"""

import numpy as np
from typing import Dict

# Lazy load sentence-transformers
_model = None

def _get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("[🔄] Loading embedding model (first run only)...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[✅] Embedding model loaded")
        except ImportError:
            raise ImportError(
                "sentence-transformers required. Install with: "
                "pip install sentence-transformers"
            )
    return _model


# Single flexible DAG template for all tasks
GENERAL_DAG = {
    "nodes": [
        {"id": "1", "primitive": "locate", "params": {"target": "input_context"}},
        {"id": "2", "primitive": "transform", "params": {"operation": "semantic_analysis"}},
        {"id": "3", "primitive": "transform", "params": {"operation": "pattern_synthesis"}},
        {"id": "4", "primitive": "validate", "params": {"check": "coherence_verify"}},
        {"id": "5", "primitive": "execute", "params": {"action": "output_generate"}},
    ],
    "edges": [
        {"from": "1", "to": "2"},
        {"from": "2", "to": "3"},
        {"from": "3", "to": "4"},
        {"from": "4", "to": "5"},
    ]
}


def embed_task(task: str) -> np.ndarray:
    """
    Generate semantic embedding for a task.
    Returns numpy array of shape (384,) for all-MiniLM-L6-v2.
    """
    model = _get_model()
    return model.encode(task)


def decompose_task(task: str) -> Dict:
    """
    Decompose a task into embedding + DAG for processing.

    Returns:
        {
            "task": original task string,
            "embedding": numpy array for clustering,
            "dag": the reasoning DAG structure,
        }
    """
    embedding = embed_task(task)

    result = {
        "task": task,
        "embedding": embedding,
        "dag": GENERAL_DAG,
    }

    print(f"[🧠] Task embedded (dim={len(embedding)})")
    print(f"[📊] Generated DAG with {len(GENERAL_DAG['nodes'])} nodes")

    return result


# ==========================================================
# === Manual Test Runner ===================================
# ==========================================================
if __name__ == "__main__":
    test_tasks = [
        "Analyze user onboarding workflow",
        "Design reinforcement learning reward function",
        "Explain the Taoist concept of Yin and Yang",
        "Describe Kantian categorical imperative",
        "Optimize inventory forecasting system",
        "Build microservices API gateway",
        "How do I cook a perfect steak?",
        "Explain quantum entanglement",
        "What is the meaning of life?"
    ]

    print("\n🧠 Semantic Task Embedding Test\n" + "="*50)

    embeddings = []
    for task in test_tasks:
        print(f"\nTask: {task}")
        result = decompose_task(task)
        embeddings.append(result["embedding"])
        print(f"  Embedding shape: {result['embedding'].shape}")
        print("-" * 50)

    # Show similarity matrix
    print("\n📊 Similarity Matrix (top 5x5):")
    embeddings = np.array(embeddings)
    sim_matrix = np.dot(embeddings, embeddings.T)
    norms = np.linalg.norm(embeddings, axis=1)
    sim_matrix = sim_matrix / np.outer(norms, norms)

    for i in range(min(5, len(test_tasks))):
        row = [f"{sim_matrix[i][j]:.2f}" for j in range(min(5, len(test_tasks)))]
        print(f"  {' '.join(row)}")

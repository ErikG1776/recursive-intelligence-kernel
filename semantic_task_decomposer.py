"""
semantic_task_decomposer.py | RIK v5.0
------------------------------------------------------------
Parses natural language tasks and generates domain-specific
reasoning DAGs, enabling meaningful abstraction clustering.

Uses sentence-transformers for semantic domain classification
instead of keyword matching.
"""

import numpy as np
from typing import Dict, Tuple

# Lazy load sentence-transformers to avoid slow startup
_model = None
_domain_embeddings = None

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

# Rich domain descriptions for semantic matching
DOMAIN_DESCRIPTIONS = {
    "business": "Business processes, workflows, customer onboarding, sales pipelines, marketing campaigns, employee management, CRM systems, invoicing, billing, stakeholder management, KPIs, ROI metrics, and enterprise operations",

    "technical": "Software development, API design, database management, server deployment, microservices architecture, containerization with Docker and Kubernetes, CI/CD pipelines, version control with Git, authentication systems, backend and frontend integration",

    "optimization": "Performance optimization, efficiency improvement, resource allocation, cost reduction, throughput maximization, latency minimization, scheduling algorithms, demand forecasting, predictive analytics, and system tuning",

    "analysis": "Data analysis, pattern detection, anomaly identification, fraud detection, research investigation, audit review, benchmarking, measurement, diagnostic assessment, and comparative evaluation",

    "ml_ai": "Machine learning, deep learning, neural networks, model training, reinforcement learning, reward functions, classification, regression, clustering, embeddings, transformers, attention mechanisms, gradient descent, hyperparameter tuning, and AI agent development",

    "philosophy": "Western philosophy, epistemology, ontology, phenomenology, ethics, logic, rational argumentation, dialectic reasoning, Socratic method, Platonic ideals, Aristotelian logic, existentialism, and analytical philosophy",

    "spirituality": "Eastern spirituality, Taoism, Yin and Yang, Zen Buddhism, meditation, enlightenment, karma, dharma, chakras, qi energy, Kabbalah, Tree of Life, mysticism, esoteric traditions, Hermeticism, alchemy, sacred geometry, transcendence, nirvana, Advaita Vedanta, and archetypal symbolism",

    "design": "System architecture, software design, UX/UI design, prototyping, wireframing, component design, design patterns, blueprints, technical specifications, interface layout, and framework architecture",

    "data": "Data engineering, ETL pipelines, data warehousing, data lakes, stream processing, batch processing, SQL and NoSQL databases, schema design, data transformation, data quality, and data ingestion"
}

def _get_domain_embeddings():
    """Compute and cache domain description embeddings."""
    global _domain_embeddings
    if _domain_embeddings is None:
        model = _get_model()
        _domain_embeddings = {}
        for domain, description in DOMAIN_DESCRIPTIONS.items():
            _domain_embeddings[domain] = model.encode(description)
    return _domain_embeddings

# Domain-specific primitive sequences (DAG templates)
DOMAIN_DAG_TEMPLATES = {
    "business": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "business_entity"}},
            {"id": "2", "primitive": "validate", "params": {"check": "business_rules"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "workflow_mapping"}},
            {"id": "4", "primitive": "execute", "params": {"action": "process_step"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
        ]
    },
    "technical": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "system_component"}},
            {"id": "2", "primitive": "validate", "params": {"check": "technical_spec"}},
            {"id": "3", "primitive": "execute", "params": {"action": "implementation"}},
            {"id": "4", "primitive": "validate", "params": {"check": "integration_test"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
        ]
    },
    "optimization": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "performance_metric"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "baseline_measure"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "optimization_apply"}},
            {"id": "4", "primitive": "validate", "params": {"check": "improvement_verify"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
        ]
    },
    "analysis": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "data_source"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "data_extraction"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "pattern_detection"}},
            {"id": "4", "primitive": "validate", "params": {"check": "findings_verify"}},
            {"id": "5", "primitive": "execute", "params": {"action": "report_generate"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
        ]
    },
    "ml_ai": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "training_data"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "feature_engineering"}},
            {"id": "3", "primitive": "execute", "params": {"action": "model_training"}},
            {"id": "4", "primitive": "validate", "params": {"check": "model_evaluation"}},
            {"id": "5", "primitive": "execute", "params": {"action": "hyperparameter_tune"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
        ]
    },
    "philosophy": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "conceptual_domain"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "logical_analysis"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "argument_mapping"}},
            {"id": "4", "primitive": "validate", "params": {"check": "coherence_verify"}},
            {"id": "5", "primitive": "execute", "params": {"action": "synthesis_generate"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
        ]
    },
    "spirituality": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "spiritual_tradition"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "symbolic_extraction"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "archetypal_mapping"}},
            {"id": "4", "primitive": "transform", "params": {"operation": "transcendent_synthesis"}},
            {"id": "5", "primitive": "validate", "params": {"check": "wisdom_coherence"}},
            {"id": "6", "primitive": "execute", "params": {"action": "insight_generate"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
            {"from": "5", "to": "6"},
        ]
    },
    "design": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "requirements"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "architecture_draft"}},
            {"id": "3", "primitive": "validate", "params": {"check": "design_review"}},
            {"id": "4", "primitive": "transform", "params": {"operation": "specification_refine"}},
            {"id": "5", "primitive": "execute", "params": {"action": "blueprint_finalize"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
        ]
    },
    "data": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "data_source"}},
            {"id": "2", "primitive": "validate", "params": {"check": "schema_verify"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "etl_process"}},
            {"id": "4", "primitive": "validate", "params": {"check": "data_quality"}},
            {"id": "5", "primitive": "execute", "params": {"action": "data_load"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "5"},
        ]
    },
    "general": {
        "nodes": [
            {"id": "1", "primitive": "locate", "params": {"target": "input"}},
            {"id": "2", "primitive": "transform", "params": {"operation": "process"}},
            {"id": "3", "primitive": "execute", "params": {"action": "complete"}},
        ],
        "edges": [
            {"from": "1", "to": "2"},
            {"from": "2", "to": "3"},
        ]
    }
}


def classify_domain(task: str) -> Tuple[str, float]:
    """
    Classify task into a domain using semantic embeddings.
    Returns (domain_name, confidence_score).
    """
    model = _get_model()
    domain_embeddings = _get_domain_embeddings()

    # Encode the task
    task_embedding = model.encode(task)

    # Compute cosine similarity with each domain
    similarities = {}
    for domain, domain_emb in domain_embeddings.items():
        # Cosine similarity
        similarity = np.dot(task_embedding, domain_emb) / (
            np.linalg.norm(task_embedding) * np.linalg.norm(domain_emb)
        )
        similarities[domain] = float(similarity)

    # Find best match
    best_domain = max(similarities, key=similarities.get)
    confidence = similarities[best_domain]

    # Normalize confidence to 0-1 range (similarities typically 0.2-0.8)
    normalized_confidence = min(max((confidence - 0.2) / 0.6, 0.0), 1.0)

    return (best_domain, round(normalized_confidence, 2))


def decompose_task(task: str) -> Dict:
    """
    Decompose a natural language task into a domain-specific reasoning DAG.

    Returns:
        {
            "task": original task string,
            "domain": detected domain,
            "confidence": classification confidence,
            "dag": the reasoning DAG structure,
            "sequence": flattened primitive sequence for clustering
        }
    """
    domain, confidence = classify_domain(task)
    dag = DOMAIN_DAG_TEMPLATES.get(domain, DOMAIN_DAG_TEMPLATES["general"])

    # Create flattened sequence for abstraction clustering
    primitives = [node["primitive"] for node in dag["nodes"]]
    params = [str(node.get("params", {})) for node in dag["nodes"]]
    sequence = f"{domain}:{'-'.join(primitives)}:{'-'.join(params)}"

    result = {
        "task": task,
        "domain": domain,
        "confidence": confidence,
        "dag": dag,
        "sequence": sequence
    }

    print(f"[🧠] Task classified → {domain} (confidence: {confidence})")
    print(f"[📊] Generated DAG with {len(dag['nodes'])} nodes")

    return result


def get_domain_description(domain: str) -> str:
    """Get human-readable description of a domain."""
    descriptions = {
        "business": "Business process and workflow tasks",
        "technical": "Software development and system integration",
        "optimization": "Performance improvement and resource optimization",
        "analysis": "Data analysis and pattern detection",
        "ml_ai": "Machine learning and AI model development",
        "philosophy": "Western philosophical and logical reasoning",
        "spirituality": "Eastern wisdom, mysticism, and sacred traditions",
        "design": "Architecture and system design",
        "data": "Data engineering and ETL pipelines",
        "general": "General-purpose task processing"
    }
    return descriptions.get(domain, "Unknown domain")


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
        "Analyze fraud detection patterns",
        "Create ETL pipeline for customer data",
        "Explore the Kabbalistic Tree of Life symbolism",
        "What is the meaning of Nietzsche's eternal return?",
        "How do I cook a perfect steak?",
        "Explain quantum entanglement"
    ]

    print("\n🧠 Semantic Task Decomposition Test (Embedding-based)\n" + "="*50)

    for task in test_tasks:
        print(f"\nTask: {task}")
        result = decompose_task(task)
        print(f"  Domain: {result['domain']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Sequence: {result['sequence'][:60]}...")
        print("-" * 50)

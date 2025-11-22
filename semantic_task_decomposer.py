"""
semantic_task_decomposer.py | RIK v5.0
------------------------------------------------------------
Parses natural language tasks and generates domain-specific
reasoning DAGs, enabling meaningful abstraction clustering.
"""

import re
from typing import Dict, List, Tuple

# Domain keyword mappings for classification
DOMAIN_KEYWORDS = {
    "business": [
        "workflow", "onboarding", "customer", "sales", "revenue", "marketing",
        "employee", "process", "pipeline", "crm", "erp", "invoice", "billing",
        "stakeholder", "roi", "kpi", "metric", "dashboard"
    ],
    "technical": [
        "api", "database", "server", "deploy", "code", "function", "class",
        "microservice", "container", "docker", "kubernetes", "ci/cd", "git",
        "endpoint", "authentication", "backend", "frontend", "integration"
    ],
    "optimization": [
        "optimize", "improve", "enhance", "efficiency", "performance", "speed",
        "reduce", "minimize", "maximize", "throughput", "latency", "cost",
        "resource", "allocation", "scheduling", "forecast", "predict"
    ],
    "analysis": [
        "analyze", "examine", "investigate", "study", "research", "evaluate",
        "assess", "review", "audit", "compare", "benchmark", "measure",
        "diagnose", "identify", "detect", "fraud", "anomaly", "pattern"
    ],
    "ml_ai": [
        "learning", "neural", "model", "training", "inference", "reinforcement",
        "reward", "agent", "classifier", "regression", "clustering", "embedding",
        "transformer", "attention", "gradient", "backprop", "loss", "accuracy"
    ],
    "philosophy": [
        "meaning", "symbolic", "metaphor", "existence", "consciousness", "ethics",
        "truth", "beauty", "wisdom", "spiritual", "soul", "mind", "being",
        "philosophy", "epistemology", "ontology", "phenomenology", "taoism"
    ],
    "design": [
        "design", "architect", "structure", "blueprint", "schema", "layout",
        "interface", "ux", "ui", "prototype", "wireframe", "component",
        "pattern", "template", "framework", "specification"
    ],
    "data": [
        "data", "etl", "pipeline", "warehouse", "lake", "transform", "ingest",
        "stream", "batch", "query", "sql", "nosql", "schema", "table",
        "column", "row", "index", "partition", "aggregation"
    ]
}

# Domain-specific primitive sequences
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
            {"id": "2", "primitive": "transform", "params": {"operation": "semantic_analysis"}},
            {"id": "3", "primitive": "transform", "params": {"operation": "symbolic_mapping"}},
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
    Classify task into a domain based on keyword matching.
    Returns (domain_name, confidence_score).
    """
    task_lower = task.lower()
    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        return ("general", 0.0)

    best_domain = max(scores, key=scores.get)
    # Normalize confidence: score / max possible (assume 3+ keywords = high confidence)
    confidence = min(scores[best_domain] / 3.0, 1.0)

    return (best_domain, round(confidence, 2))


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
    # This is what gets stored and clustered
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
        "philosophy": "Philosophical and conceptual reasoning",
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
        "Describe the symbolic meaning of the Tree of Life",
        "Optimize inventory forecasting system",
        "Build microservices API gateway",
        "Analyze fraud detection patterns",
        "Create ETL pipeline for customer data"
    ]

    print("\n🧠 Semantic Task Decomposition Test\n" + "="*50)

    for task in test_tasks:
        print(f"\nTask: {task}")
        result = decompose_task(task)
        print(f"  Domain: {result['domain']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Sequence: {result['sequence'][:60]}...")
        print("-" * 50)

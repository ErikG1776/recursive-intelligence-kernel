"""
test_reasoning.py | Unit tests for reasoning.py
-----------------------------------------------
Tests for task grammar validation, abstraction, and analogy
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reasoning


class TestTaskGrammarValidation:
    """Test task schema validation"""

    def test_valid_task_schema(self):
        """Test validation of a valid task"""
        valid_task = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"selector": "#login"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [
                {"from": "n1", "to": "n2", "condition": "success"}
            ]
        }

        result = reasoning.validate_task_schema(valid_task)
        assert result == True

    def test_missing_required_fields(self):
        """Test validation fails for missing required fields"""
        invalid_task = {
            "nodes": [
                {"id": "n1"}  # Missing 'primitive' field
            ],
            "edges": []
        }

        result = reasoning.validate_task_schema(invalid_task)
        assert result == False

    def test_invalid_primitive_type(self):
        """Test validation fails for invalid primitive type"""
        invalid_task = {
            "nodes": [
                {"id": "n1", "primitive": "invalid_type"}  # Not in enum
            ],
            "edges": []
        }

        result = reasoning.validate_task_schema(invalid_task)
        assert result == False

    def test_missing_nodes(self):
        """Test validation fails when nodes are missing"""
        invalid_task = {
            "edges": []
        }

        result = reasoning.validate_task_schema(invalid_task)
        assert result == False

    def test_valid_all_primitives(self):
        """Test all valid primitive types"""
        valid_task = {
            "nodes": [
                {"id": "n1", "primitive": "locate"},
                {"id": "n2", "primitive": "transform"},
                {"id": "n3", "primitive": "validate"},
                {"id": "n4", "primitive": "execute"}
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
                {"from": "n3", "to": "n4"}
            ]
        }

        result = reasoning.validate_task_schema(valid_task)
        assert result == True


class TestAnalogyValidation:
    """Test analogy validation between tasks"""

    def test_identical_tasks_high_similarity(self):
        """Test identical tasks have high similarity"""
        task1 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }

        task2 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }

        is_analog, score = reasoning.validate_analogy(task1, task2, threshold=0.5)
        assert is_analog == True
        assert score >= 0.9  # Should be very high for identical tasks

    def test_different_structure_low_similarity(self):
        """Test structurally different tasks have low similarity"""
        task1 = {
            "nodes": [
                {"id": "n1", "primitive": "locate"}
            ],
            "edges": []
        }

        task2 = {
            "nodes": [
                {"id": "n1", "primitive": "locate"},
                {"id": "n2", "primitive": "transform"},
                {"id": "n3", "primitive": "validate"}
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"}
            ]
        }

        is_analog, score = reasoning.validate_analogy(task1, task2, threshold=0.8)
        assert is_analog == False

    def test_similar_tasks_moderate_similarity(self):
        """Test similar but not identical tasks"""
        task1 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "login button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }

        task2 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "submit button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }

        is_analog, score = reasoning.validate_analogy(task1, task2, threshold=0.3)
        assert is_analog == True
        assert 0.3 <= score <= 1.0


class TestGraphOperations:
    """Test graph building and analysis"""

    def test_build_graph_creates_nodes(self):
        """Test graph building creates correct nodes"""
        task = {
            "nodes": [
                {"id": "n1", "primitive": "locate"},
                {"id": "n2", "primitive": "transform"}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }

        graph = reasoning.build_graph(task)

        assert "n1" in graph.nodes()
        assert "n2" in graph.nodes()
        assert graph.has_edge("n1", "n2")

    def test_build_graph_preserves_edge_count(self):
        """Test graph has correct number of edges"""
        task = {
            "nodes": [
                {"id": "n1", "primitive": "locate"},
                {"id": "n2", "primitive": "transform"},
                {"id": "n3", "primitive": "validate"}
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"}
            ]
        }

        graph = reasoning.build_graph(task)

        assert len(graph.nodes()) == 3
        assert len(graph.edges()) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

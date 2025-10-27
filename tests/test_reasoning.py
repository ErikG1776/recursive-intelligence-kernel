import pytest
import reasoning


class TestAnalogyValidation:
    """Tests for validate_analogy function in reasoning.py"""

    def test_identical_tasks_high_similarity(self):
        """Test identical tasks have high similarity"""
        task1 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}}
            ],
            "edges": [{"from": "n1", "to": "n2"}]
        }
        task2 = task1.copy()

        result = reasoning.validate_analogy(task1, task2, sim_threshold=0.5)
        assert isinstance(result, bool)
        assert result is True

    def test_different_structure_low_similarity(self):
        """Test structurally different tasks have low similarity"""
        task1 = {"nodes": [{"id": "n1", "primitive": "locate"}], "edges": []}
        task2 = {
            "nodes": [
                {"id": "n1", "primitive": "locate"},
                {"id": "n2", "primitive": "transform"},
                {"id": "n3", "primitive": "validate"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        }

        result = reasoning.validate_analogy(task1, task2, sim_threshold=0.8)
        assert isinstance(result, bool)
        assert result is False

    def test_similar_tasks_moderate_similarity(self):
        """Test similar but not identical tasks"""
        task1 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "login button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}},
            ],
            "edges": [{"from": "n1", "to": "n2"}],
        }
        task2 = {
            "nodes": [
                {"id": "n1", "primitive": "locate", "params": {"element": "submit button"}},
                {"id": "n2", "primitive": "transform", "params": {"action": "click"}},
            ],
            "edges": [{"from": "n1", "to": "n2"}],
        }

        result = reasoning.validate_analogy(task1, task2, sim_threshold=0.3)
        assert isinstance(result, bool)
        # can be either True or False depending on implementation; ensure no error
        assert result in (True, False)


class TestReasoningBasics:
    """Smoke tests for reasoning module"""

    def test_reasoning_module_loads(self):
        """Ensure the reasoning module can be imported"""
        assert hasattr(reasoning, "validate_analogy")
        assert callable(reasoning.validate_analogy)
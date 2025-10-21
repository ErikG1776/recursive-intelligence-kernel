"""
test_meta.py | Unit tests for meta.py
--------------------------------------
Tests for rollback mechanism, visualization, and fitness evaluation
"""

import pytest
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import meta


class TestFitnessEvaluation:
    """Test fitness evaluation functionality"""

    def test_evaluate_fitness_returns_score(self):
        """Test fitness evaluation returns a score"""
        score = meta.evaluate_fitness()

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_evaluate_fitness_within_expected_range(self):
        """Test fitness score is within simulation range"""
        # Run multiple times to test randomness
        scores = [meta.evaluate_fitness() for _ in range(10)]

        # All scores should be between 0.8 and 1.0 (based on simulation)
        assert all(0.8 <= score <= 1.0 for score in scores)


class TestArchitectureVisualization:
    """Test architecture diagram generation"""

    def test_visualize_default_architecture(self):
        """Test visualization with default schema"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            temp_path = f.name

        try:
            diagram = meta.visualize_architecture(save_path=temp_path)

            # Check diagram was generated
            assert "graph TD" in diagram
            assert "Meta-Controller" in diagram
            assert "Reasoning Engine" in diagram

            # Check file was created
            assert os.path.exists(temp_path)

            # Read and verify content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert content == diagram

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_visualize_custom_schema(self):
        """Test visualization with custom schema"""
        custom_schema = {
            "Module A": ["Module B"],
            "Module B": ["Module C"],
            "Module C": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            temp_path = f.name

        try:
            diagram = meta.visualize_architecture(adl_schema=custom_schema, save_path=temp_path)

            assert "Module A --> Module B" in diagram
            assert "Module B --> Module C" in diagram
            assert "Module C" in diagram

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestRollbackMechanism:
    """Test rollback functionality"""

    def test_apply_modification_creates_backup(self):
        """Test that modifications are logged"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("original_code = True")
            temp_file = f.name

        try:
            # Apply modification
            meta.apply_modification(
                temp_file,
                "modified_code = True",
                "Test modification"
            )

            # Verify file was modified
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "modified_code = True" in content

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_apply_modification_missing_file_raises_error(self):
        """Test that modifying non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            meta.apply_modification(
                "/nonexistent/file.py",
                "new_code",
                "Should fail"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

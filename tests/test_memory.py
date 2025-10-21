"""
test_memory.py | Unit tests for memory.py
-------------------------------------------
Tests for episodic memory, semantic search, and consolidation
"""

import pytest
import os
import sqlite3
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import memory
from exceptions import DatabaseException


@pytest.fixture
def temp_db(monkeypatch):
    """Create a temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_memory.db")

    # Monkey-patch get_db_path to use temp database
    monkeypatch.setattr(memory, 'get_db_path', lambda: temp_db_path)

    # Initialize the database
    memory.init_memory_db()

    yield temp_db_path

    # Cleanup
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    os.rmdir(temp_dir)


class TestMemoryInitialization:
    """Test database initialization"""

    def test_init_creates_all_tables(self, temp_db):
        """Test that init_memory_db creates all required tables"""
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()

        # Check all tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in c.fetchall()}

        assert 'episodes' in tables
        assert 'episodic_memory' in tables
        assert 'modifications' in tables
        assert 'strategy_weights' in tables

        conn.close()

    def test_episodes_table_schema(self, temp_db):
        """Test episodes table has correct schema"""
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()

        c.execute("PRAGMA table_info(episodes)")
        columns = {row[1]: row[2] for row in c.fetchall()}

        assert 'id' in columns
        assert 'timestamp' in columns
        assert 'task' in columns
        assert 'result' in columns
        assert 'reflection' in columns

        conn.close()


class TestEpisodicMemory:
    """Test episodic memory operations"""

    def test_save_episode(self, temp_db):
        """Test saving an episode"""
        memory.save_episode("Test task", "success", "Test reflection")

        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM episodes")
        count = c.fetchone()[0]

        assert count == 1
        conn.close()

    def test_get_recent_episodes(self, temp_db):
        """Test retrieving recent episodes"""
        # Add some test episodes
        for i in range(5):
            memory.save_episode(f"Task {i}", "success", f"Reflection {i}")

        episodes = memory.get_recent_episodes(limit=3)

        assert len(episodes) == 3
        assert episodes[0]['task'] == "Task 4"  # Most recent first
        assert 'timestamp' in episodes[0]
        assert 'reflection' in episodes[0]

    def test_get_recent_episodes_empty_db(self, temp_db):
        """Test getting episodes from empty database"""
        episodes = memory.get_recent_episodes()
        assert episodes == []


class TestSemanticSearch:
    """Test semantic search functionality"""

    def test_retrieve_context_with_similar_tasks(self, temp_db):
        """Test semantic search finds similar tasks"""
        # Add diverse episodes
        memory.save_episode("Fix login bug", "success", "Resolved authentication issue")
        memory.save_episode("Update user profile", "success", "Added new fields")
        memory.save_episode("Debug authentication", "success", "Fixed session timeout")

        # Search for authentication-related task
        result = memory.retrieve_context("authentication problem", top_k=2)

        assert result['context'] is not None
        assert 'similar_episodes' in result
        assert len(result['similar_episodes']) <= 2

        # Most similar should be authentication-related
        top_match = result['similar_episodes'][0]
        assert 'authentication' in top_match['task'].lower() or \
               'authentication' in top_match['reflection'].lower()

    def test_retrieve_context_empty_db(self, temp_db):
        """Test semantic search on empty database"""
        result = memory.retrieve_context("test task")

        assert result['context'] is None
        assert result['similar_episodes'] == []

    def test_retrieve_context_single_episode(self, temp_db):
        """Test semantic search with only one episode"""
        memory.save_episode("Single task", "success", "Single reflection")

        result = memory.retrieve_context("query")

        assert result['context'] == "Single reflection"
        assert len(result['similar_episodes']) == 1
        assert result['similar_episodes'][0]['similarity'] == 1.0


class TestConsolidation:
    """Test episode consolidation"""

    def test_consolidate_insufficient_data(self, temp_db):
        """Test consolidation with insufficient data"""
        memory.save_episode("Task 1", "success", "Reflection 1")

        result = memory.consolidate_episodes(min_samples=2)

        assert result['consolidated'] == False
        assert result['reason'] == 'insufficient_data'

    def test_consolidate_creates_clusters(self, temp_db):
        """Test consolidation creates clusters from similar episodes"""
        # Add similar authentication episodes
        for i in range(3):
            memory.save_episode(
                f"Fix authentication bug {i}",
                "success",
                f"Resolved auth issue {i}"
            )

        # Add different UI episodes
        for i in range(3):
            memory.save_episode(
                f"Update UI component {i}",
                "success",
                f"Improved interface {i}"
            )

        result = memory.consolidate_episodes(eps=0.5, min_samples=2)

        assert result['consolidated'] == True
        assert result['total_episodes'] == 6
        assert result['clusters_formed'] >= 1


class TestDatabaseExceptions:
    """Test error handling"""

    def test_get_recent_episodes_invalid_db(self, monkeypatch):
        """Test exception handling for invalid database"""
        # Point to non-existent database
        monkeypatch.setattr(memory, 'get_db_path', lambda: '/nonexistent/path.db')

        with pytest.raises(DatabaseException):
            memory.get_recent_episodes()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

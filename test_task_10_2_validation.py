"""
Test validation for Task 10.2: Create checkpoint load function

This test file validates the load_checkpoint() function implementation
according to the requirements and design specifications.

Requirements validated:
- 14.4: When restarting after interruption, the Scraper shall read the
  checkpoint file to identify completed Search_Queries

Test cases:
1. Load checkpoint from existing valid file
2. Return empty list when file doesn't exist
3. Handle corrupted JSON gracefully
4. Handle missing 'completed_queries' field
5. Support UTF-8 encoded queries
"""

import pytest
import json
import os
import tempfile
from scraper import load_checkpoint


class TestLoadCheckpoint:
    """Test suite for load_checkpoint function"""
    
    def test_load_valid_checkpoint(self, tmp_path):
        """Test loading a valid checkpoint file with completed queries"""
        # Create a valid checkpoint file
        checkpoint_path = tmp_path / "checkpoint.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [
                "software engineer Bangalore",
                "python developer Bangalore",
                "data analyst Bangalore"
            ],
            "total_jobs_collected": 287
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 3
        assert result == [
            "software engineer Bangalore",
            "python developer Bangalore",
            "data analyst Bangalore"
        ]
    
    def test_load_nonexistent_checkpoint(self, tmp_path):
        """Test loading checkpoint when file doesn't exist - should return empty list"""
        checkpoint_path = tmp_path / "nonexistent.json"
        
        # Load checkpoint (file doesn't exist)
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify returns empty list
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []
    
    def test_load_corrupted_checkpoint(self, tmp_path):
        """Test loading checkpoint with invalid JSON - should return empty list"""
        checkpoint_path = tmp_path / "corrupted.json"
        
        # Create corrupted JSON file
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content }")
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify returns empty list
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []
    
    def test_load_checkpoint_missing_field(self, tmp_path):
        """Test loading checkpoint without 'completed_queries' field - should return empty list"""
        checkpoint_path = tmp_path / "missing_field.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "total_jobs_collected": 100
            # Missing 'completed_queries' field
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify returns empty list
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []
    
    def test_load_checkpoint_empty_queries(self, tmp_path):
        """Test loading checkpoint with empty completed_queries list"""
        checkpoint_path = tmp_path / "empty_queries.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [],
            "total_jobs_collected": 0
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify returns empty list
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []
    
    def test_load_checkpoint_utf8_queries(self, tmp_path):
        """Test loading checkpoint with UTF-8 encoded queries (international characters)"""
        checkpoint_path = tmp_path / "utf8_checkpoint.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [
                "software engineer Bangalore",
                "développeur python Paris",  # French
                "データサイエンティスト 東京"  # Japanese
            ],
            "total_jobs_collected": 150
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify UTF-8 queries are loaded correctly
        assert isinstance(result, list)
        assert len(result) == 3
        assert "développeur python Paris" in result
        assert "データサイエンティスト 東京" in result
    
    def test_load_checkpoint_single_query(self, tmp_path):
        """Test loading checkpoint with single completed query"""
        checkpoint_path = tmp_path / "single_query.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": ["software engineer Bangalore"],
            "total_jobs_collected": 50
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "software engineer Bangalore"
    
    def test_load_checkpoint_preserves_order(self, tmp_path):
        """Test that load_checkpoint preserves the order of queries"""
        checkpoint_path = tmp_path / "ordered_checkpoint.json"
        queries = [
            "query 1",
            "query 2",
            "query 3",
            "query 4",
            "query 5"
        ]
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": queries,
            "total_jobs_collected": 200
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify order is preserved
        assert result == queries
    
    def test_load_checkpoint_with_special_characters(self, tmp_path):
        """Test loading checkpoint with queries containing special characters"""
        checkpoint_path = tmp_path / "special_chars.json"
        checkpoint_data = {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [
                "C++ developer Bangalore",
                "software engineer (remote)",
                "data analyst - Bangalore",
                "full-stack developer @ startup"
            ],
            "total_jobs_collected": 100
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f)
        
        # Load checkpoint
        result = load_checkpoint(str(checkpoint_path))
        
        # Verify special characters are preserved
        assert len(result) == 4
        assert "C++ developer Bangalore" in result
        assert "software engineer (remote)" in result
        assert "data analyst - Bangalore" in result
        assert "full-stack developer @ startup" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

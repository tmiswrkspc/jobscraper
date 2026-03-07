"""
Validation tests for Task 10.1: Create checkpoint save function

This test file validates the save_checkpoint() function implementation.
Tests verify that the function correctly saves checkpoint data including
completed queries, timestamp, and total jobs collected.

Requirements validated: 14.1, 14.2
"""

import json
import os
import tempfile
import shutil
from datetime import datetime
from scraper import save_checkpoint


def test_save_checkpoint_creates_file():
    """Test that save_checkpoint creates a checkpoint file."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(temp_dir, 'test_checkpoint.json')
        completed_queries = ["software engineer Bangalore", "python developer Bangalore"]
        total_jobs = 287
        
        # Save checkpoint
        save_checkpoint(completed_queries, checkpoint_path, total_jobs)
        
        # Verify file was created
        assert os.path.exists(checkpoint_path), "Checkpoint file was not created"
        
        # Verify file contains valid JSON
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify data structure
        assert 'timestamp' in data, "Checkpoint missing timestamp field"
        assert 'completed_queries' in data, "Checkpoint missing completed_queries field"
        assert 'total_jobs_collected' in data, "Checkpoint missing total_jobs_collected field"
        
        # Verify data values
        assert data['completed_queries'] == completed_queries, "Completed queries don't match"
        assert data['total_jobs_collected'] == total_jobs, "Total jobs count doesn't match"
        
        # Verify timestamp format (ISO 8601)
        timestamp = datetime.fromisoformat(data['timestamp'])
        assert isinstance(timestamp, datetime), "Timestamp is not valid ISO 8601 format"
        
        print("✓ save_checkpoint creates file with correct structure")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_save_checkpoint_creates_directory():
    """Test that save_checkpoint creates checkpoint directory if it doesn't exist."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Use nested directory that doesn't exist
        checkpoint_path = os.path.join(temp_dir, 'checkpoints', 'session.json')
        completed_queries = ["data analyst Bangalore"]
        
        # Save checkpoint (should create directory)
        save_checkpoint(completed_queries, checkpoint_path, 42)
        
        # Verify directory was created
        checkpoint_dir = os.path.dirname(checkpoint_path)
        assert os.path.exists(checkpoint_dir), "Checkpoint directory was not created"
        
        # Verify file was created
        assert os.path.exists(checkpoint_path), "Checkpoint file was not created"
        
        print("✓ save_checkpoint creates directory if it doesn't exist")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_save_checkpoint_overwrites_existing():
    """Test that save_checkpoint overwrites existing checkpoint file."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(temp_dir, 'checkpoint.json')
        
        # Save first checkpoint
        first_queries = ["query1"]
        save_checkpoint(first_queries, checkpoint_path, 100)
        
        # Read first checkpoint
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            first_data = json.load(f)
        
        # Save second checkpoint (should overwrite)
        second_queries = ["query1", "query2", "query3"]
        save_checkpoint(second_queries, checkpoint_path, 350)
        
        # Read second checkpoint
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            second_data = json.load(f)
        
        # Verify second checkpoint overwrote first
        assert second_data['completed_queries'] == second_queries, "Queries not updated"
        assert second_data['total_jobs_collected'] == 350, "Total jobs not updated"
        assert second_data['timestamp'] != first_data['timestamp'], "Timestamp not updated"
        
        print("✓ save_checkpoint overwrites existing checkpoint")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_save_checkpoint_empty_queries():
    """Test that save_checkpoint handles empty completed queries list."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(temp_dir, 'checkpoint.json')
        
        # Save checkpoint with empty queries
        save_checkpoint([], checkpoint_path, 0)
        
        # Verify file was created
        assert os.path.exists(checkpoint_path), "Checkpoint file was not created"
        
        # Read checkpoint
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify empty list is saved correctly
        assert data['completed_queries'] == [], "Empty queries list not saved correctly"
        assert data['total_jobs_collected'] == 0, "Total jobs should be 0"
        
        print("✓ save_checkpoint handles empty queries list")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_save_checkpoint_unicode_queries():
    """Test that save_checkpoint handles Unicode characters in queries."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(temp_dir, 'checkpoint.json')
        
        # Save checkpoint with Unicode queries
        unicode_queries = ["software engineer Bengaluru", "डेटा साइंटिस्ट", "développeur Python"]
        save_checkpoint(unicode_queries, checkpoint_path, 150)
        
        # Read checkpoint
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify Unicode queries are preserved
        assert data['completed_queries'] == unicode_queries, "Unicode queries not preserved"
        
        print("✓ save_checkpoint handles Unicode characters")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_save_checkpoint_default_total_jobs():
    """Test that save_checkpoint uses default value for total_jobs parameter."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(temp_dir, 'checkpoint.json')
        
        # Save checkpoint without total_jobs parameter
        save_checkpoint(["query1"], checkpoint_path)
        
        # Read checkpoint
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify default value is used
        assert data['total_jobs_collected'] == 0, "Default total_jobs should be 0"
        
        print("✓ save_checkpoint uses default total_jobs value")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("Running Task 10.1 validation tests...\n")
    
    test_save_checkpoint_creates_file()
    test_save_checkpoint_creates_directory()
    test_save_checkpoint_overwrites_existing()
    test_save_checkpoint_empty_queries()
    test_save_checkpoint_unicode_queries()
    test_save_checkpoint_default_total_jobs()
    
    print("\n✅ All Task 10.1 validation tests passed!")

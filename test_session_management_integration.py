"""
Integration test for session management functions (Tasks 10.1, 10.2, 10.3)

This test validates that save_checkpoint(), load_checkpoint(), and
save_intermediate_results() work together correctly for session resumption.
"""

import json
import os
import tempfile
import shutil
from scraper import save_checkpoint, load_checkpoint, save_intermediate_results


def test_full_session_management_workflow():
    """
    Test complete session management workflow:
    1. Save intermediate results after query 1
    2. Save checkpoint after query 1
    3. Save intermediate results after query 2
    4. Save checkpoint after query 2
    5. Simulate interruption
    6. Load checkpoint to resume
    7. Load intermediate results
    8. Continue from where left off
    """
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(test_dir, 'session_checkpoint.json')
        intermediate_path = os.path.join(test_dir, 'intermediate_results.json')
        
        # === Phase 1: First query completes ===
        print("Phase 1: Query 1 completes")
        
        query1_jobs = [
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job1'
            },
            {
                'title': 'Senior Engineer',
                'company': 'Innovation Labs',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job2'
            }
        ]
        
        accumulated_jobs = query1_jobs.copy()
        completed_queries = ['software engineer Bangalore']
        
        # Save intermediate results and checkpoint
        save_intermediate_results(accumulated_jobs, intermediate_path)
        save_checkpoint(completed_queries, checkpoint_path, len(accumulated_jobs))
        
        print(f"  ✓ Saved {len(accumulated_jobs)} jobs")
        print(f"  ✓ Checkpoint: {completed_queries}")
        
        # === Phase 2: Second query completes ===
        print("\nPhase 2: Query 2 completes")
        
        query2_jobs = [
            {
                'title': 'Python Developer',
                'company': 'Software Solutions',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job3'
            },
            {
                'title': 'Backend Engineer',
                'company': 'Data Systems',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job4'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Web Tech',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job5'
            }
        ]
        
        accumulated_jobs.extend(query2_jobs)
        completed_queries.append('python developer Bangalore')
        
        # Save intermediate results and checkpoint
        save_intermediate_results(accumulated_jobs, intermediate_path)
        save_checkpoint(completed_queries, checkpoint_path, len(accumulated_jobs))
        
        print(f"  ✓ Saved {len(accumulated_jobs)} jobs total")
        print(f"  ✓ Checkpoint: {completed_queries}")
        
        # === Phase 3: Simulate interruption and recovery ===
        print("\nPhase 3: Simulating interruption...")
        print("  [Session interrupted]")
        
        print("\nPhase 4: Resuming session")
        
        # Load checkpoint
        loaded_queries = load_checkpoint(checkpoint_path)
        print(f"  ✓ Loaded checkpoint: {len(loaded_queries)} queries completed")
        
        # Load intermediate results
        with open(intermediate_path, 'r', encoding='utf-8') as f:
            recovered_jobs = json.load(f)
        print(f"  ✓ Recovered {len(recovered_jobs)} jobs")
        
        # === Verification ===
        print("\nVerification:")
        
        # Verify checkpoint data
        assert len(loaded_queries) == 2, f"Expected 2 queries, got {len(loaded_queries)}"
        assert loaded_queries[0] == 'software engineer Bangalore'
        assert loaded_queries[1] == 'python developer Bangalore'
        print("  ✓ Checkpoint data correct")
        
        # Verify intermediate results
        assert len(recovered_jobs) == 5, f"Expected 5 jobs, got {len(recovered_jobs)}"
        assert recovered_jobs[0]['title'] == 'Software Engineer'
        assert recovered_jobs[2]['title'] == 'Python Developer'
        assert recovered_jobs[4]['title'] == 'Full Stack Developer'
        print("  ✓ Intermediate results correct")
        
        # Verify all job fields preserved
        for job in recovered_jobs:
            assert 'title' in job
            assert 'company' in job
            assert 'location' in job
            assert 'link' in job
        print("  ✓ All job fields preserved")
        
        # === Phase 5: Continue from checkpoint ===
        print("\nPhase 5: Continuing from checkpoint")
        
        all_queries = [
            'software engineer Bangalore',
            'python developer Bangalore',
            'data analyst Bangalore',  # This one should be processed
            'frontend developer Bangalore'  # This one should be processed
        ]
        
        remaining_queries = [q for q in all_queries if q not in loaded_queries]
        print(f"  ✓ Remaining queries to process: {remaining_queries}")
        
        assert len(remaining_queries) == 2
        assert 'data analyst Bangalore' in remaining_queries
        assert 'frontend developer Bangalore' in remaining_queries
        print("  ✓ Correctly identified remaining queries")
        
        print("\n✅ Full session management workflow test passed!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_session_management_with_utf8():
    """Test session management with UTF-8 characters (₹ rupee symbol)."""
    test_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(test_dir, 'session_checkpoint.json')
        intermediate_path = os.path.join(test_dir, 'intermediate_results.json')
        
        # Jobs with UTF-8 characters
        jobs = [
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=job1',
                'salary': '₹8,00,000 - ₹12,00,000 a year'
            }
        ]
        
        # Save with UTF-8 characters
        save_intermediate_results(jobs, intermediate_path)
        save_checkpoint(['software engineer Bangalore'], checkpoint_path, len(jobs))
        
        # Load and verify UTF-8 preservation
        with open(intermediate_path, 'r', encoding='utf-8') as f:
            loaded_jobs = json.load(f)
        
        assert loaded_jobs[0]['salary'] == '₹8,00,000 - ₹12,00,000 a year'
        assert '₹' in loaded_jobs[0]['salary']
        
        print("✅ UTF-8 encoding test passed!")
        
    finally:
        shutil.rmtree(test_dir)


def test_session_management_empty_state():
    """Test session management with empty initial state."""
    test_dir = tempfile.mkdtemp()
    
    try:
        checkpoint_path = os.path.join(test_dir, 'session_checkpoint.json')
        intermediate_path = os.path.join(test_dir, 'intermediate_results.json')
        
        # Save empty state
        save_intermediate_results([], intermediate_path)
        save_checkpoint([], checkpoint_path, 0)
        
        # Load empty state
        loaded_queries = load_checkpoint(checkpoint_path)
        with open(intermediate_path, 'r', encoding='utf-8') as f:
            loaded_jobs = json.load(f)
        
        assert loaded_queries == []
        assert loaded_jobs == []
        
        print("✅ Empty state test passed!")
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("=" * 70)
    print("Session Management Integration Tests")
    print("=" * 70)
    print()
    
    test_full_session_management_workflow()
    print()
    test_session_management_with_utf8()
    print()
    test_session_management_empty_state()
    
    print()
    print("=" * 70)
    print("✅ All integration tests passed!")
    print("=" * 70)

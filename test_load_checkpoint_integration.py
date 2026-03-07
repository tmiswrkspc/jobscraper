"""
Integration test for load_checkpoint with actual checkpoint file

This test verifies that load_checkpoint works correctly with the
actual checkpoint file in the checkpoints directory.
"""

from scraper import load_checkpoint


def test_load_actual_checkpoint():
    """Test loading the actual checkpoint file"""
    checkpoint_path = "checkpoints/session_checkpoint.json"
    
    # Load checkpoint
    completed_queries = load_checkpoint(checkpoint_path)
    
    # Verify result
    print(f"\nLoaded {len(completed_queries)} completed queries:")
    for i, query in enumerate(completed_queries, 1):
        print(f"  {i}. {query}")
    
    # Basic validation
    assert isinstance(completed_queries, list)
    assert len(completed_queries) > 0
    assert all(isinstance(q, str) for q in completed_queries)
    
    print("\n✓ Successfully loaded checkpoint file!")
    print(f"✓ Found {len(completed_queries)} completed queries")


if __name__ == "__main__":
    test_load_actual_checkpoint()

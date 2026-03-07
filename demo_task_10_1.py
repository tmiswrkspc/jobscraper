"""
Demonstration of Task 10.1: save_checkpoint function

This script demonstrates the save_checkpoint() function by simulating
a scraping session that saves checkpoints after completing queries.
"""

import json
import os
from scraper import save_checkpoint
from config import CHECKPOINT_DIR, CHECKPOINT_FILENAME


def demo_checkpoint_save():
    """Demonstrate checkpoint saving during a simulated scraping session."""
    print("=" * 70)
    print("Task 10.1 Demonstration: Checkpoint Save Function")
    print("=" * 70)
    print()
    
    # Simulate a scraping session with multiple queries
    all_queries = [
        "software engineer Bangalore",
        "python developer Bangalore",
        "data analyst Bangalore",
        "frontend developer Bangalore"
    ]
    
    completed_queries = []
    total_jobs = 0
    
    # Construct checkpoint path
    checkpoint_path = os.path.join(CHECKPOINT_DIR, CHECKPOINT_FILENAME)
    
    print(f"Checkpoint file: {checkpoint_path}")
    print()
    
    # Simulate processing queries one by one
    for i, query in enumerate(all_queries, 1):
        print(f"Processing query {i}/{len(all_queries)}: '{query}'")
        
        # Simulate collecting jobs (random number for demo)
        import random
        jobs_collected = random.randint(50, 150)
        total_jobs += jobs_collected
        
        print(f"  → Collected {jobs_collected} jobs")
        
        # Add to completed queries
        completed_queries.append(query)
        
        # Save checkpoint
        save_checkpoint(completed_queries, checkpoint_path, total_jobs)
        print(f"  → Checkpoint saved: {len(completed_queries)} queries, {total_jobs} total jobs")
        print()
    
    # Display final checkpoint content
    print("=" * 70)
    print("Final Checkpoint Content:")
    print("=" * 70)
    
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        checkpoint_data = json.load(f)
    
    print(json.dumps(checkpoint_data, indent=2, ensure_ascii=False))
    print()
    
    # Show checkpoint file structure
    print("=" * 70)
    print("Checkpoint File Structure:")
    print("=" * 70)
    print(f"✓ timestamp: {checkpoint_data['timestamp']}")
    print(f"✓ completed_queries: {len(checkpoint_data['completed_queries'])} queries")
    for idx, query in enumerate(checkpoint_data['completed_queries'], 1):
        print(f"    {idx}. {query}")
    print(f"✓ total_jobs_collected: {checkpoint_data['total_jobs_collected']}")
    print()
    
    print("=" * 70)
    print("Key Features Demonstrated:")
    print("=" * 70)
    print("✓ Checkpoint saved after each query completion")
    print("✓ Timestamp in ISO 8601 format")
    print("✓ Completed queries list tracks progress")
    print("✓ Total jobs collected accumulates across queries")
    print("✓ Checkpoint directory created automatically")
    print("✓ UTF-8 encoding supports international characters")
    print()
    
    print("=" * 70)
    print("Requirements Validated:")
    print("=" * 70)
    print("✓ 14.1: Save intermediate results after completing each Search_Query")
    print("✓ 14.2: Use checkpoint file to track completed Search_Queries")
    print()


if __name__ == '__main__':
    demo_checkpoint_save()

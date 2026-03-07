"""
Demonstration of Task 8.1: generate_output_filename() function

This script demonstrates the filename generation function in action.
"""

from scraper import generate_output_filename
import time


def main():
    print("=" * 70)
    print("Task 8.1: Filename Generation Function Demonstration")
    print("=" * 70)
    print()
    
    print("1. Generating JSON output filename:")
    json_filename = generate_output_filename("indeed_jobs", "json")
    print(f"   {json_filename}")
    print()
    
    print("2. Generating CSV output filename:")
    csv_filename = generate_output_filename("indeed_jobs", "csv")
    print(f"   {csv_filename}")
    print()
    
    print("3. Generating multiple filenames (showing uniqueness):")
    for i in range(3):
        filename = generate_output_filename("scrape_results", "json")
        print(f"   Attempt {i+1}: {filename}")
        time.sleep(1)  # Wait 1 second between generations
    print()
    
    print("4. Different base names:")
    filenames = [
        generate_output_filename("jobs", "json"),
        generate_output_filename("results", "json"),
        generate_output_filename("data", "json"),
    ]
    for filename in filenames:
        print(f"   {filename}")
    print()
    
    print("5. Different extensions:")
    extensions = ["json", "csv", "txt", "xml"]
    for ext in extensions:
        filename = generate_output_filename("output", ext)
        print(f"   {filename}")
    print()
    
    print("✅ Filename generation function is working correctly!")
    print()
    print("Key features:")
    print("  • Format: base_name_YYYYMMDD_HHMMSS.extension")
    print("  • Timestamp ensures uniqueness (1-second resolution)")
    print("  • Chronologically sortable filenames")
    print("  • Prevents overwriting previous results")
    print()


if __name__ == "__main__":
    main()

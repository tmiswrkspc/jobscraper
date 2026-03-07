"""
Demonstration of Task 11.2: handle_captcha_detection function

This script demonstrates the CAPTCHA handling function in action,
showing how it logs warnings and tracks consecutive CAPTCHAs.
"""

import logging
from scraper import handle_captcha_detection

# Configure logging to show all levels
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

def demo_captcha_handling():
    """Demonstrate CAPTCHA handling with various scenarios."""
    
    print("=" * 70)
    print("DEMO: CAPTCHA Handling Function")
    print("=" * 70)
    print()
    
    # Scenario 1: Single CAPTCHA detection
    print("Scenario 1: Single CAPTCHA Detection")
    print("-" * 70)
    consecutive = 0
    query = "software engineer Bangalore"
    consecutive = handle_captcha_detection(query, 1, consecutive)
    print(f"Consecutive count after 1st CAPTCHA: {consecutive}")
    print()
    
    # Scenario 2: Two consecutive CAPTCHAs
    print("Scenario 2: Two Consecutive CAPTCHAs")
    print("-" * 70)
    consecutive = handle_captcha_detection(query, 2, consecutive)
    print(f"Consecutive count after 2nd CAPTCHA: {consecutive}")
    print()
    
    # Scenario 3: Third CAPTCHA triggers critical warning
    print("Scenario 3: Third CAPTCHA (Critical Warning Triggered)")
    print("-" * 70)
    consecutive = handle_captcha_detection(query, 3, consecutive)
    print(f"Consecutive count after 3rd CAPTCHA: {consecutive}")
    print()
    
    # Scenario 4: Fourth CAPTCHA (still critical)
    print("Scenario 4: Fourth CAPTCHA (Still Critical)")
    print("-" * 70)
    consecutive = handle_captcha_detection(query, 4, consecutive)
    print(f"Consecutive count after 4th CAPTCHA: {consecutive}")
    print()
    
    # Scenario 5: Reset after successful page load
    print("Scenario 5: Reset After Successful Page Load")
    print("-" * 70)
    print("(In actual usage, caller would reset consecutive to 0)")
    consecutive = 0
    print(f"Consecutive count reset to: {consecutive}")
    print()
    
    # Scenario 6: New CAPTCHA after reset
    print("Scenario 6: New CAPTCHA After Reset")
    print("-" * 70)
    query = "python developer Bangalore"
    consecutive = handle_captcha_detection(query, 1, consecutive)
    print(f"Consecutive count after reset: {consecutive}")
    print()
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key Observations:")
    print("1. Each CAPTCHA detection logs a WARNING with query and page number")
    print("2. Consecutive count is tracked and returned")
    print("3. At threshold (3), a CRITICAL warning is logged")
    print("4. Caller is responsible for resetting count on successful page loads")
    print()


if __name__ == "__main__":
    demo_captcha_handling()

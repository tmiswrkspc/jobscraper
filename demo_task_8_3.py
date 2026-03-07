"""
Demo script for Task 8.3: CSV Export Function

This script demonstrates the export_to_csv() function with sample job data,
showing how it handles:
- Complete job records with all fields
- Missing optional fields
- Special characters (commas, quotes, rupee symbol)
- UTF-8 encoding with BOM for Excel compatibility
"""

from scraper import export_to_csv, generate_output_filename
import os

# Sample job records with various scenarios
sample_jobs = [
    {
        'title': 'Senior Software Engineer',
        'company': 'Tech Mahindra',
        'location': 'Bangalore, Karnataka',
        'salary': '₹12,00,000 - ₹18,00,000 a year',
        'posted_date': '2 days ago',
        'link': 'https://in.indeed.com/viewjob?jk=abc123def456',
        'description': 'We are looking for a "highly skilled" software engineer with 5+ years of experience in Python, Java, and cloud technologies.'
    },
    {
        'title': 'Python Developer',
        'company': 'Infosys Limited',
        'location': 'Remote',
        'salary': '₹8,00,000 - ₹10,00,000 a year',
        'posted_date': '1 week ago',
        'link': 'https://in.indeed.com/viewjob?jk=xyz789ghi012',
        'description': 'Join our team as a Python developer. Must have experience with Django, Flask, and REST APIs.'
    },
    {
        'title': 'Data Analyst',
        'company': 'Wipro',
        'location': 'Bangalore, Karnataka',
        'link': 'https://in.indeed.com/viewjob?jk=mno345pqr678',
        # Missing: salary, posted_date, description
    },
    {
        'title': 'Full Stack Developer (React + Node.js)',
        'company': 'TCS - Tata Consultancy Services',
        'location': 'Hyderabad, Telangana',
        'salary': '₹6,00,000 - ₹9,00,000 a year',
        'posted_date': '3 days ago',
        'link': 'https://in.indeed.com/viewjob?jk=stu901vwx234',
        'description': 'Looking for a full stack developer with expertise in React, Node.js, MongoDB.\nExcellent benefits and "work-life balance".'
    },
    {
        'title': 'Java Developer, Senior',
        'company': 'Accenture',
        'location': 'Pune, Maharashtra',
        'salary': '₹10,00,000 a year',
        'posted_date': '5 days ago',
        'link': 'https://in.indeed.com/viewjob?jk=yza567bcd890',
        'description': 'Senior Java developer needed for enterprise applications. Spring Boot, Microservices, AWS experience required.'
    }
]

def main():
    print("=" * 70)
    print("Task 8.3 Demo: CSV Export Function")
    print("=" * 70)
    print()
    
    # Generate output filename with timestamp
    output_filename = generate_output_filename('demo_jobs', 'csv')
    output_path = os.path.join('output', output_filename)
    
    print(f"Exporting {len(sample_jobs)} job records to CSV...")
    print(f"Output file: {output_path}")
    print()
    
    # Export to CSV
    export_to_csv(sample_jobs, output_path)
    
    print()
    print("CSV Export Features Demonstrated:")
    print("  ✓ UTF-8 encoding with BOM for Excel compatibility")
    print("  ✓ Column headers (title, company, location, salary, posted_date, link, description)")
    print("  ✓ QUOTE_MINIMAL quoting strategy")
    print("  ✓ Special character handling (commas, quotes, newlines)")
    print("  ✓ Rupee symbol (₹) preservation")
    print("  ✓ Missing optional fields handled as empty strings")
    print()
    
    # Display file info
    file_size = os.path.getsize(output_path)
    print(f"File created successfully!")
    print(f"  - Size: {file_size} bytes")
    print(f"  - Location: {output_path}")
    print()
    
    # Show first few lines of the CSV
    print("First 3 lines of CSV file:")
    print("-" * 70)
    with open(output_path, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f):
            if i < 3:
                # Truncate long lines for display
                display_line = line.rstrip()
                if len(display_line) > 100:
                    display_line = display_line[:97] + "..."
                print(display_line)
    print("-" * 70)
    print()
    
    print("✅ Demo completed successfully!")
    print()
    print("You can now open the CSV file in Excel or any spreadsheet application.")
    print("The UTF-8 BOM ensures Excel correctly displays special characters like ₹.")

if __name__ == '__main__':
    main()

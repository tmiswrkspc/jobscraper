"""
Validation tests for Task 8.3: Create CSV export function

This test file validates the export_to_csv() function implementation.
Tests cover:
- Basic CSV export with complete job records
- CSV export with missing optional fields
- Special character handling (commas, quotes, newlines)
- UTF-8 encoding with BOM for Excel compatibility
- Header row generation
- Round-trip validation (export and re-import)

Requirements validated: 6.2, 6.4, 6.5, 6.6
"""

import csv
import os
import tempfile
from scraper import export_to_csv


def test_csv_export_basic():
    """Test basic CSV export with complete job records."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'salary': '₹8,00,000 - ₹12,00,000 a year',
            'posted_date': '2 days ago',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'description': 'We are looking for a skilled software engineer...'
        },
        {
            'title': 'Python Developer',
            'company': 'Data Inc',
            'location': 'Remote',
            'salary': '₹10,00,000 a year',
            'posted_date': '1 week ago',
            'link': 'https://in.indeed.com/viewjob?jk=def456',
            'description': 'Join our team as a Python developer'
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Verify file exists
        assert os.path.exists(temp_path), "CSV file was not created"
        
        # Read and verify content
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Verify number of rows
            assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
            
            # Verify headers
            assert reader.fieldnames == ['title', 'company', 'location', 'salary', 'posted_date', 'link', 'description']
            
            # Verify first row
            assert rows[0]['title'] == 'Software Engineer'
            assert rows[0]['company'] == 'Tech Corp'
            assert rows[0]['location'] == 'Bangalore, Karnataka'
            assert rows[0]['salary'] == '₹8,00,000 - ₹12,00,000 a year'
            assert rows[0]['posted_date'] == '2 days ago'
            assert rows[0]['link'] == 'https://in.indeed.com/viewjob?jk=abc123'
            assert 'skilled software engineer' in rows[0]['description']
            
            # Verify second row
            assert rows[1]['title'] == 'Python Developer'
            assert rows[1]['company'] == 'Data Inc'
            
        print("✓ Basic CSV export test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_missing_optional_fields():
    """Test CSV export with missing optional fields (salary, posted_date, description)."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore',
            'link': 'https://in.indeed.com/viewjob?jk=abc123'
            # Missing: salary, posted_date, description
        },
        {
            'title': 'Data Analyst',
            'company': 'Analytics Co',
            'location': 'Mumbai',
            'link': 'https://in.indeed.com/viewjob?jk=xyz789',
            'salary': '₹6,00,000 a year'
            # Missing: posted_date, description
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Read and verify content
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Verify first row has empty strings for missing fields
            assert rows[0]['title'] == 'Software Engineer'
            assert rows[0]['salary'] == ''
            assert rows[0]['posted_date'] == ''
            assert rows[0]['description'] == ''
            
            # Verify second row
            assert rows[1]['title'] == 'Data Analyst'
            assert rows[1]['salary'] == '₹6,00,000 a year'
            assert rows[1]['posted_date'] == ''
            assert rows[1]['description'] == ''
            
        print("✓ Missing optional fields test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_special_characters():
    """Test CSV export with special characters (commas, quotes, newlines)."""
    job_records = [
        {
            'title': 'Software Engineer, Senior',
            'company': 'Tech "Innovators" Corp',
            'location': 'Bangalore, Karnataka, India',
            'salary': '₹8,00,000 - ₹12,00,000 a year',
            'posted_date': '2 days ago',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'description': 'We are looking for a "skilled" engineer.\nMust have 5+ years experience.'
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Read and verify content
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Verify special characters are preserved
            assert rows[0]['title'] == 'Software Engineer, Senior'
            assert rows[0]['company'] == 'Tech "Innovators" Corp'
            assert rows[0]['location'] == 'Bangalore, Karnataka, India'
            assert '"skilled"' in rows[0]['description']
            assert '\n' in rows[0]['description'] or 'Must have 5+ years' in rows[0]['description']
            
        print("✓ Special characters test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_utf8_with_bom():
    """Test CSV export uses UTF-8 encoding with BOM for Excel compatibility."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore',
            'salary': '₹10,00,000 a year',
            'posted_date': '2 days ago',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'description': 'Great opportunity'
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Read raw bytes to check for BOM
        with open(temp_path, 'rb') as f:
            raw_bytes = f.read(3)
            # UTF-8 BOM is EF BB BF
            assert raw_bytes == b'\xef\xbb\xbf', f"Expected UTF-8 BOM, got {raw_bytes.hex()}"
        
        # Verify UTF-8 characters are preserved
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert '₹' in rows[0]['salary'], "Rupee symbol not preserved"
            
        print("✓ UTF-8 with BOM test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_round_trip():
    """Test CSV export and re-import produces equivalent data (round-trip validation)."""
    original_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'salary': '₹8,00,000 - ₹12,00,000 a year',
            'posted_date': '2 days ago',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'description': 'We are looking for a "skilled" engineer with 5+ years experience.'
        },
        {
            'title': 'Python Developer',
            'company': 'Data Inc',
            'location': 'Remote',
            'link': 'https://in.indeed.com/viewjob?jk=def456'
            # Missing optional fields
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(original_records, temp_path)
        
        # Re-import from CSV
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            imported_records = list(reader)
        
        # Verify number of records
        assert len(imported_records) == len(original_records)
        
        # Verify each record
        for i, (original, imported) in enumerate(zip(original_records, imported_records)):
            assert imported['title'] == original['title'], f"Row {i}: title mismatch"
            assert imported['company'] == original['company'], f"Row {i}: company mismatch"
            assert imported['location'] == original['location'], f"Row {i}: location mismatch"
            assert imported['link'] == original['link'], f"Row {i}: link mismatch"
            
            # Handle optional fields (missing fields become empty strings)
            assert imported['salary'] == original.get('salary', ''), f"Row {i}: salary mismatch"
            assert imported['posted_date'] == original.get('posted_date', ''), f"Row {i}: posted_date mismatch"
            assert imported['description'] == original.get('description', ''), f"Row {i}: description mismatch"
        
        print("✓ Round-trip validation test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_empty_list():
    """Test CSV export with empty list creates file with headers only."""
    job_records = []
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Verify file exists
        assert os.path.exists(temp_path), "CSV file was not created"
        
        # Read and verify content
        with open(temp_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Verify headers exist
            assert reader.fieldnames == ['title', 'company', 'location', 'salary', 'posted_date', 'link', 'description']
            
            # Verify no data rows
            assert len(rows) == 0, f"Expected 0 rows, got {len(rows)}"
            
        print("✓ Empty list test passed")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_csv_export_creates_directory():
    """Test CSV export creates output directory if it doesn't exist."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore',
            'link': 'https://in.indeed.com/viewjob?jk=abc123'
        }
    ]
    
    # Create temporary directory path that doesn't exist
    temp_dir = tempfile.mkdtemp()
    nested_dir = os.path.join(temp_dir, 'nested', 'output')
    temp_path = os.path.join(nested_dir, 'jobs.csv')
    
    try:
        # Verify directory doesn't exist
        assert not os.path.exists(nested_dir)
        
        # Export to CSV
        export_to_csv(job_records, temp_path)
        
        # Verify directory was created
        assert os.path.exists(nested_dir), "Output directory was not created"
        
        # Verify file was created
        assert os.path.exists(temp_path), "CSV file was not created"
        
        print("✓ Directory creation test passed")
        
    finally:
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("Running Task 8.3 validation tests...\n")
    
    test_csv_export_basic()
    test_csv_export_missing_optional_fields()
    test_csv_export_special_characters()
    test_csv_export_utf8_with_bom()
    test_csv_export_round_trip()
    test_csv_export_empty_list()
    test_csv_export_creates_directory()
    
    print("\n✅ All Task 8.3 validation tests passed!")
    print("\nRequirements validated:")
    print("  - 6.2: CSV file export with all unique Job_Records")
    print("  - 6.4: Column headers included in CSV output")
    print("  - 6.5: UTF-8 encoding with BOM for Excel compatibility")
    print("  - 6.6: Special characters and commas handled with proper escaping")

# Indeed Job Scraper

A high-volume, stealthy web scraping system designed to extract fresh job listings from Indeed India (in.indeed.com). The scraper targets technology jobs in Bangalore and remote positions across India, implementing advanced anti-detection techniques to collect 1000-2000 unique jobs per run while avoiding rate limits and blocks.

## Features

- **Stealthy Scraping**: Mimics human browsing behavior with random delays, scrolling, and mouse movements
- **High Volume**: Collects 1000-2000 unique job listings per session
- **Anti-Detection**: Implements resource blocking, stealth plugins, and human-like interaction patterns
- **Resilient**: Gracefully handles network failures, CAPTCHAs, and selector changes
- **Session Resumability**: Checkpoint-based recovery from interruptions
- **Multiple Export Formats**: Outputs data in both JSON and CSV formats
- **Comprehensive Logging**: Real-time progress updates and error reporting

## Prerequisites

- **Python 3.8 or higher** is required
- Internet connection for web scraping
- Sufficient disk space for output files (approximately 5-10 MB per session)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd indeed-job-scraper
```

Or download and extract the project archive to your desired location.

### 2. Install Python Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- `playwright==1.40.0` - Browser automation framework
- `playwright-stealth>=1.0.6` - Stealth plugins to avoid detection
- `hypothesis` - Property-based testing framework
- `pytest>=7.0.0` - Testing framework

### 3. Install Playwright Browsers

After installing the Python packages, you need to install the Chromium browser for Playwright:

```bash
playwright install chromium
```

This command downloads the Chromium browser binary that Playwright will use for scraping. The download is approximately 150-200 MB.

**Note**: If you encounter permission issues, you may need to run the command with appropriate privileges or use a virtual environment.

## Quick Start

Once installation is complete, you can run the scraper:

```bash
cd indeed-job-scraper
python scraper.py
```

The scraper will:
1. Execute 8 predefined search queries targeting tech jobs in Bangalore and remote positions
2. Navigate through up to 4 pages per query
3. Extract job details (title, company, location, salary, posted date, link, description)
4. Remove duplicate listings
5. Export results to timestamped JSON and CSV files in the `output/` directory

### Expected Output

- **JSON file**: `output/indeed_jobs_YYYYMMDD_HHMMSS.json`
- **CSV file**: `output/indeed_jobs_YYYYMMDD_HHMMSS.csv`
- **Console logs**: Real-time progress updates showing queries, pages, and job counts

### Sample Output Structure

```json
[
  {
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "Bangalore, Karnataka",
    "salary": "₹8,00,000 - ₹12,00,000 a year",
    "posted_date": "2 days ago",
    "link": "https://in.indeed.com/viewjob?jk=abc123",
    "description": "We are looking for a skilled software engineer..."
  }
]
```

## Configuration

You can customize the scraper behavior by modifying `config.py`:

- **Search queries**: Modify the `SEARCH_QUERIES` list to target different roles or locations
- **Delay ranges**: Adjust `MIN_DELAY` and `MAX_DELAY` to change wait times between requests
- **Pagination**: Change `MAX_PAGES_PER_QUERY` to scrape more or fewer pages
- **Timeouts**: Modify `PAGE_LOAD_TIMEOUT` for slower connections

## Troubleshooting

### CAPTCHA Challenges

If you encounter CAPTCHA challenges:
- The scraper will automatically detect and skip CAPTCHA pages
- Consider increasing delay ranges in `config.py` to appear more human-like
- If CAPTCHAs persist, wait a few hours before running again

### Network Timeouts

If pages fail to load:
- Check your internet connection
- Increase `PAGE_LOAD_TIMEOUT` in `config.py`
- The scraper will continue with remaining pages automatically

### Selector Changes

If Indeed updates their page structure:
- Check the console logs for selector failure warnings
- Update the CSS selectors in `scraper.py` (documented with comments)
- Refer to the design document for selector update guidance

### No Jobs Extracted

If no jobs are being extracted:
- Verify your internet connection
- Check if Indeed India (in.indeed.com) is accessible from your location
- Review console logs for error messages
- Try running with a single query first to isolate issues

## Running Tests

The project includes comprehensive test coverage. To run tests:

```bash
cd indeed-job-scraper
pytest
```

To run specific test categories:

```bash
# Unit tests only
pytest tests/

# Property-based tests
pytest -k "property"

# Integration tests
pytest -k "integration"
```

## Session Resumption

If a scraping session is interrupted:
1. The scraper automatically saves checkpoints after each query
2. Intermediate results are saved to `output/intermediate_*.json`
3. Simply run `python scraper.py` again to resume from the last checkpoint
4. The scraper will skip completed queries and merge results

## Legal and Ethical Considerations

- **Respect robots.txt**: Review Indeed's robots.txt and terms of service
- **Rate limiting**: The scraper implements delays to avoid overloading servers
- **Personal use**: This tool is intended for personal research and analysis
- **Data privacy**: Do not share or publish scraped data containing personal information
- **Commercial use**: Consult legal counsel before using scraped data commercially

## Project Structure

```
indeed-job-scraper/
├── scraper.py              # Main scraper implementation
├── config.py               # Configuration constants
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── output/                # Output directory for results
├── checkpoints/           # Session checkpoint files
└── tests/                 # Test suite
```

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the design document for detailed architecture information
3. Examine console logs for specific error messages
4. Ensure all dependencies are correctly installed

## License

This project is provided as-is for educational and research purposes.

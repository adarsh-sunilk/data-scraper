# Clinical Trials Data Scraper

A Python-based data scraper for retrieving clinical trials information from ClinicalTrials.gov API. This tool extracts comprehensive data about interventional clinical trials conducted by pharmaceutical companies, including trial phases, recruitment status, conditions treated, and intervention details.

## Features

- **Comprehensive Data Extraction**: Retrieves detailed information about clinical trials including:
  - Company/Sponsor information
  - Trial phases (Phase 0, 1, 2, 3, 4) with start/end dates
  - Recruitment status (Recruiting, Completed, Terminated, etc.)
  - Conditions treated
  - Interventions/Treatments
  - Study locations and demographics

- **Flexible Search Options**: 
  - Text-based search queries
  - Filter by trial phases, recruitment status, conditions, sponsors, countries
  - Support for complex search criteria

- **Multiple Export Formats**:
  - CSV format for spreadsheet analysis
  - JSON format for programmatic use
  - Both formats simultaneously

- **Data Processing**:
  - Structured data models using Pydantic
  - Data validation and cleaning
  - Summary reports and statistics

- **Command-Line Interface**: Easy-to-use CLI with various options and filters

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd data-scrapper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create output directory** (optional):
   ```bash
   mkdir data
   ```

## Quick Start

### Basic Usage

Search for clinical trials with a simple query:

```bash
python main.py --query "cancer treatment" --max-results 100
```

### Advanced Search with Filters

Search with specific criteria:

```bash
python main.py \
  --query "immunotherapy" \
  --phases PHASE1 PHASE2 \
  --status RECRUITING ACTIVE_NOT_RECRUITING \
  --conditions cancer oncology \
  --countries "United States" \
  --max-results 500
```

### Get Specific Trial Details

Retrieve detailed information for a specific trial:

```bash
python main.py get-trial NCT12345678
```

### Export Options

Export data in different formats:

```bash
# Export to CSV only
python main.py --query "diabetes" --output-format csv

# Export to JSON only  
python main.py --query "diabetes" --output-format json

# Export to both formats
python main.py --query "diabetes" --output-format both
```

## Data Fields Retrieved

The scraper extracts the following information for each clinical trial:

### Basic Information
- **NCT ID**: Unique identifier
- **Brief Title**: Short descriptive title
- **Official Title**: Complete official title
- **Study Type**: Type of study (Interventional, Observational, etc.)

### Trial Phases
- **Current Phase**: Active trial phases
- **Phase Dates**: Start and end dates for each phase (0, 1, 2, 3, 4)

### Status Information
- **Recruitment Status**: Current recruitment status including:
  - Not yet recruiting
  - Recruiting
  - Enrolling by invitation
  - Active, not recruiting
  - Suspended
  - Terminated
  - Completed
  - Withdrawn
  - Unknown

### Study Details
- **Conditions Treated**: Medical conditions being studied
- **Interventions/Treatments**: Drugs, devices, or procedures being tested
- **Sponsors**: Lead sponsor and collaborators
- **Locations**: Study sites and facilities
- **Enrollment**: Number of participants
- **Study Population**: Target population description

### Dates
- **Start Date**: Trial start date
- **Completion Date**: Trial completion date
- **Primary Completion Date**: Primary endpoint completion date

## Configuration

The scraper can be configured through the `config.py` file:

```python
# API Configuration
CLINICAL_TRIALS_API_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
MAX_RESULTS_PER_REQUEST = 1000
REQUEST_DELAY = 1.0  # seconds between requests

# Output Configuration
OUTPUT_DIRECTORY = "./data"
OUTPUT_FORMAT = "csv"  # csv, json, or both
```

## Command Line Options

### Main Command Options

- `--query, -q`: Search query for clinical trials
- `--max-results, -m`: Maximum number of results to retrieve (default: 1000)
- `--phases, -p`: Filter by trial phases (PHASE0, PHASE1, PHASE2, PHASE3, PHASE4)
- `--status, -s`: Filter by recruitment status
- `--conditions, -c`: Filter by medical conditions
- `--sponsors`: Filter by sponsor names (comma-separated)
- `--countries`: Filter by countries (comma-separated)
- `--output-format, -f`: Output format (csv, json, both)
- `--output-dir, -o`: Output directory for exported files
- `--verbose, -v`: Enable verbose logging

### Get Trial Command Options

- `nct_id`: NCT identifier (required)
- `--output-format, -f`: Output format (csv, json, both)
- `--output-dir, -o`: Output directory for exported files

## Examples

### Example 1: Search for Cancer Trials

```bash
python main.py \
  --query "cancer treatment" \
  --phases PHASE2 PHASE3 \
  --status RECRUITING COMPLETED \
  --max-results 200 \
  --output-format both
```

### Example 2: Search by Pharmaceutical Company

```bash
python main.py \
  --query "sponsor:Pfizer" \
  --conditions diabetes \
  --max-results 100
```

### Example 3: Search by Country and Status

```bash
python main.py \
  --query "immunotherapy" \
  --countries "United States" "Canada" \
  --status RECRUITING \
  --max-results 150
```

## Programmatic Usage

You can also use the scraper programmatically:

```python
from clinical_trials_api import ClinicalTrialsAPI
from data_processor import DataProcessor
from models import SearchFilters

# Initialize API client
api = ClinicalTrialsAPI()

# Search for trials
trials = api.search_trials(
    query="cancer treatment",
    max_results=100
)

# Export data
processor = DataProcessor("./data")
files = processor.export_trials(trials, format_type="csv")
```

## Output Files

The scraper creates timestamped files in the specified output directory:

- `clinical_trials_YYYYMMDD_HHMMSS.csv`: CSV format data
- `clinical_trials_YYYYMMDD_HHMMSS.json`: JSON format data
- `trial_NCT12345678_YYYYMMDD_HHMMSS.*`: Individual trial files

## Data Source

This scraper uses the [ClinicalTrials.gov API v2](https://clinicaltrials.gov/api/v2/docs), which provides free access to clinical trial data from the U.S. National Library of Medicine.

## Rate Limiting

The scraper includes built-in rate limiting to be respectful to the API:
- 1-second delay between requests (configurable)
- Automatic retry logic for failed requests
- User-Agent identification for API requests

## Requirements

- Python 3.8+
- Internet connection for API access
- Required packages listed in `requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of use for the ClinicalTrials.gov API and ensure compliance with any applicable data usage policies.

## Disclaimer

This tool is provided for educational and research purposes only. The data retrieved is from publicly available sources and should be used responsibly. Always verify information from official sources and consult with appropriate professionals for medical or research decisions.

"""
Configuration settings for the Clinical Trials Data Scraper
"""
import os
from typing import Literal

# API Configuration
CLINICAL_TRIALS_API_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
MAX_RESULTS_PER_REQUEST = 1000
REQUEST_DELAY = 1.0  # seconds between requests

# Output Configuration
OUTPUT_DIRECTORY = "./data"
OUTPUT_FORMAT: Literal["csv", "json", "both"] = "csv"

# Search Parameters
DEFAULT_SEARCH_TERMS = [
    "interventional",
    "clinical trial",
    "phase 1",
    "phase 2", 
    "phase 3",
    "phase 4"
]

# Field mappings for data extraction
TRIAL_FIELDS = {
    "nctId": "NCT ID",
    "briefTitle": "Brief Title",
    "officialTitle": "Official Title",
    "status": "Recruitment Status",
    "phase": "Phase",
    "startDate": "Start Date",
    "completionDate": "Completion Date",
    "conditions": "Conditions Treated",
    "interventions": "Interventions/Treatments",
    "sponsors": "Sponsors",
    "locations": "Study Locations"
}

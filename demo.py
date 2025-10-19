#!/usr/bin/env python3
"""
Demonstration script for Clinical Trials Data Scraper
This script shows various ways to use the scraper programmatically
"""

from clinical_trials_api import ClinicalTrialsAPI
from data_processor import DataProcessor
from models import SearchFilters
import json

def demo_basic_search():
    """Demonstrate basic search functionality"""
    print("=== Basic Search Demo ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Search for cancer trials
    print("Searching for cancer trials...")
    trials = api.search_trials(query="cancer", max_results=5)
    
    print(f"Found {len(trials)} trials")
    
    # Display first trial details
    if trials:
        trial = trials[0]
        print(f"\nFirst trial:")
        print(f"  NCT ID: {trial.nct_id}")
        print(f"  Title: {trial.brief_title}")
        print(f"  Status: {trial.status}")
        print(f"  Phase: {trial.current_phase}")
        print(f"  Start Date: {trial.start_date}")
        print(f"  Conditions: {', '.join([c.name for c in trial.conditions])}")
        print(f"  Sponsors: {', '.join([s.name for s in trial.sponsors])}")

def demo_filtered_search():
    """Demonstrate filtered search functionality"""
    print("\n=== Filtered Search Demo ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Create search filters
    filters = SearchFilters(
        phases=["PHASE2", "PHASE3"],
        status=["RECRUITING", "ACTIVE_NOT_RECRUITING"],
        conditions=["diabetes"]
    )
    
    print("Searching for diabetes trials in Phase 2 or 3 that are recruiting...")
    trials = api.search_trials(
        query="diabetes treatment",
        filters=filters,
        max_results=3
    )
    
    print(f"Found {len(trials)} trials matching filters")
    
    for i, trial in enumerate(trials, 1):
        print(f"\nTrial {i}:")
        print(f"  NCT ID: {trial.nct_id}")
        print(f"  Title: {trial.brief_title}")
        print(f"  Status: {trial.status}")
        print(f"  Phase: {trial.current_phase}")

def demo_export_functionality():
    """Demonstrate data export functionality"""
    print("\n=== Export Functionality Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = DataProcessor("./demo_data")
    
    # Search for trials
    print("Searching for immunotherapy trials...")
    trials = api.search_trials(query="immunotherapy", max_results=3)
    
    print(f"Found {len(trials)} trials")
    
    # Export to both formats
    print("Exporting to CSV and JSON...")
    files = processor.export_trials(
        trials=trials,
        format_type="both",
        filename_prefix="immunotherapy_demo"
    )
    
    print(f"Files created: {files}")
    
    # Create summary report
    summary = processor.create_summary_report(trials)
    print(f"\nSummary Report:")
    print(f"  Total trials: {summary['total_trials']}")
    print(f"  Status distribution: {summary['status_distribution']}")
    print(f"  Phase distribution: {summary['phase_distribution']}")

def demo_single_trial():
    """Demonstrate single trial retrieval"""
    print("\n=== Single Trial Demo ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Get a specific trial (using a known NCT ID)
    nct_id = "NCT02587312"  # This should be a real NCT ID
    print(f"Retrieving trial {nct_id}...")
    
    trial = api.get_trial_details(nct_id)
    
    if trial:
        print(f"Trial found: {trial.brief_title}")
        print(f"  Official Title: {trial.official_title}")
        print(f"  Status: {trial.status}")
        print(f"  Phase: {trial.current_phase}")
        print(f"  Start Date: {trial.start_date}")
        print(f"  Completion Date: {trial.completion_date}")
        print(f"  Conditions: {', '.join([c.name for c in trial.conditions])}")
        print(f"  Interventions: {', '.join([i.name for i in trial.interventions])}")
        print(f"  Sponsors: {', '.join([s.name for s in trial.sponsors])}")
        print(f"  Locations: {', '.join([f'{l.facility}, {l.city}, {l.country}' for l in trial.locations])}")
    else:
        print(f"Trial {nct_id} not found")

def demo_pharmaceutical_companies():
    """Demonstrate searching by pharmaceutical companies"""
    print("\n=== Pharmaceutical Companies Demo ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Search for trials by specific companies
    companies = ["Pfizer", "Merck", "Johnson & Johnson"]
    
    all_trials = []
    for company in companies:
        print(f"Searching for trials by {company}...")
        
        trials = api.search_trials(
            query=f"sponsor:{company}",
            max_results=2
        )
        
        print(f"  Found {len(trials)} trials")
        all_trials.extend(trials)
    
    print(f"\nTotal trials found across all companies: {len(all_trials)}")
    
    # Export all trials
    processor = DataProcessor("./demo_data")
    files = processor.export_trials(
        trials=all_trials,
        format_type="csv",
        filename_prefix="pharma_companies_demo"
    )
    print(f"Files created: {files}")

def main():
    """Run all demonstrations"""
    print("Clinical Trials Data Scraper - Demonstration")
    print("=" * 50)
    
    try:
        # Run demonstrations
        demo_basic_search()
        demo_filtered_search()
        demo_export_functionality()
        demo_single_trial()
        demo_pharmaceutical_companies()
        
        print("\n" + "=" * 50)
        print("✅ All demonstrations completed successfully!")
        print("\nYou can now use the scraper with:")
        print("  python3 main.py search --query 'your search term' --max-results 100")
        print("  python3 main.py get-trial NCT12345678")
        print("  python3 example_usage.py")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()

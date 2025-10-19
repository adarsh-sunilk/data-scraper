"""
Example usage of the Clinical Trials Data Scraper
"""
from clinical_trials_api import ClinicalTrialsAPI
from data_processor import DataProcessor
from models import SearchFilters
from datetime import datetime

def example_basic_search():
    """Example: Basic search for clinical trials"""
    print("=== Basic Search Example ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Search for interventional trials
    trials = api.search_trials(
        query="cancer treatment",
        max_results=50
    )
    
    print(f"Found {len(trials)} trials")
    
    # Display first few results
    for i, trial in enumerate(trials[:3]):
        print(f"\n{i+1}. {trial.brief_title}")
        print(f"   NCT ID: {trial.nct_id}")
        print(f"   Status: {trial.status}")
        print(f"   Phase: {trial.current_phase}")
        print(f"   Conditions: {', '.join([c['name'] for c in trial.conditions])}")


def example_filtered_search():
    """Example: Search with filters"""
    print("\n=== Filtered Search Example ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Create search filters
    filters = SearchFilters(
        phases=["PHASE1", "PHASE2"],
        status=["RECRUITING", "ACTIVE_NOT_RECRUITING"],
        conditions=["cancer", "oncology"],
        countries=["United States"]
    )
    
    # Search with filters
    trials = api.search_trials(
        query="immunotherapy",
        filters=filters,
        max_results=30
    )
    
    print(f"Found {len(trials)} trials matching filters")
    
    # Display results
    for i, trial in enumerate(trials[:2]):
        print(f"\n{i+1}. {trial.brief_title}")
        print(f"   NCT ID: {trial.nct_id}")
        print(f"   Status: {trial.status}")
        print(f"   Phase: {trial.current_phase}")
        print(f"   Start Date: {trial.start_date}")


def example_single_trial():
    """Example: Get details for a specific trial"""
    print("\n=== Single Trial Example ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Get specific trial (example NCT ID)
    nct_id = "NCT00000000"  # Replace with actual NCT ID
    trial = api.get_trial_details(nct_id)
    
    if trial:
        print(f"Trial: {trial.brief_title}")
        print(f"Official Title: {trial.official_title}")
        print(f"Status: {trial.status}")
        print(f"Phase: {trial.current_phase}")
        print(f"Start Date: {trial.start_date}")
        print(f"Completion Date: {trial.completion_date}")
        print(f"Conditions: {', '.join([c['name'] for c in trial.conditions])}")
        print(f"Interventions: {', '.join([i['name'] for i in trial.interventions])}")
        print(f"Sponsors: {', '.join([s['name'] for s in trial.sponsors])}")
    else:
        print(f"Trial {nct_id} not found")


def example_export_data():
    """Example: Export data to different formats"""
    print("\n=== Export Data Example ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = DataProcessor("./data")
    
    # Search for trials
    trials = api.search_trials(
        query="diabetes treatment",
        max_results=20
    )
    
    print(f"Found {len(trials)} trials")
    
    # Export to CSV
    csv_files = processor.export_trials(
        trials=trials,
        format_type="csv",
        filename_prefix="diabetes_trials"
    )
    print(f"CSV files created: {csv_files}")
    
    # Export to JSON
    json_files = processor.export_trials(
        trials=trials,
        format_type="json",
        filename_prefix="diabetes_trials"
    )
    print(f"JSON files created: {json_files}")
    
    # Create summary report
    summary = processor.create_summary_report(trials)
    print(f"\nSummary:")
    print(f"  Total trials: {summary['total_trials']}")
    print(f"  Status distribution: {summary['status_distribution']}")
    print(f"  Phase distribution: {summary['phase_distribution']}")


def example_pharmaceutical_companies():
    """Example: Search for trials by specific pharmaceutical companies"""
    print("\n=== Pharmaceutical Companies Example ===")
    
    # Initialize API client
    api = ClinicalTrialsAPI()
    
    # Search for trials by specific companies
    companies = ["Pfizer", "Merck", "Johnson & Johnson", "Novartis", "Roche"]
    
    all_trials = []
    for company in companies:
        print(f"Searching for trials by {company}...")
        
        trials = api.search_trials(
            query=f"sponsor:{company}",
            max_results=20
        )
        
        print(f"  Found {len(trials)} trials")
        all_trials.extend(trials)
    
    print(f"\nTotal trials found: {len(all_trials)}")
    
    # Export all trials
    processor = DataProcessor("./data")
    files = processor.export_trials(
        trials=all_trials,
        format_type="both",
        filename_prefix="pharma_trials"
    )
    print(f"Files created: {files}")


if __name__ == "__main__":
    print("Clinical Trials Data Scraper - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_basic_search()
    example_filtered_search()
    example_single_trial()
    example_export_data()
    example_pharmaceutical_companies()
    
    print("\n" + "=" * 50)
    print("Examples completed!")

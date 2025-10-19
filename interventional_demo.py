#!/usr/bin/env python3
"""
Demonstration script for Interventional Clinical Trials Data Scraper
This script shows how to use the specialized interventional trials processor
"""

from clinical_trials_api import ClinicalTrialsAPI
from interventional_trials_processor import InterventionalTrialsProcessor
from models import SearchFilters
import json

def demo_interventional_trials_search():
    """Demonstrate searching specifically for interventional trials"""
    print("=== Interventional Trials Search Demo ===")
    
    # Initialize API client and specialized processor
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for cancer trials
    print("Searching for cancer trials...")
    trials = api.search_trials(query="cancer", max_results=20)
    
    print(f"Found {len(trials)} total trials")
    
    # Filter for interventional trials only
    interventional_trials = processor.filter_interventional_trials(trials)
    print(f"Found {len(interventional_trials)} interventional trials")
    
    # Display first few interventional trials
    for i, trial in enumerate(interventional_trials[:3], 1):
        print(f"\nInterventional Trial {i}:")
        print(f"  NCT ID: {trial.nct_id}")
        print(f"  Title: {trial.brief_title}")
        print(f"  Study Type: {trial.study_type}")
        print(f"  Phase: {trial.current_phase}")
        print(f"  Status: {trial.status}")
        print(f"  Interventions: {', '.join([i.name for i in trial.interventions])}")
        print(f"  Is Interventional: {processor._is_interventional_trial(trial)}")

def demo_intervention_type_analysis():
    """Demonstrate analysis by intervention type"""
    print("\n=== Intervention Type Analysis Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for diabetes trials
    print("Searching for diabetes trials...")
    trials = api.search_trials(query="diabetes treatment", max_results=30)
    
    # Filter for interventional trials
    interventional_trials = processor.filter_interventional_trials(trials)
    print(f"Found {len(interventional_trials)} interventional diabetes trials")
    
    # Analyze intervention types
    intervention_analysis = {
        'Drug Interventions': sum(1 for trial in interventional_trials if processor._has_drug_intervention(trial)),
        'Device Interventions': sum(1 for trial in interventional_trials if processor._has_device_intervention(trial)),
        'Procedure Interventions': sum(1 for trial in interventional_trials if processor._has_procedure_intervention(trial)),
        'Behavioral Interventions': sum(1 for trial in interventional_trials if processor._has_behavioral_intervention(trial)),
        'Biological Interventions': sum(1 for trial in interventional_trials if processor._has_biological_intervention(trial)),
        'Radiation Interventions': sum(1 for trial in interventional_trials if processor._has_radiation_intervention(trial)),
    }
    
    print(f"\nIntervention Type Analysis:")
    for intervention_type, count in intervention_analysis.items():
        percentage = (count / len(interventional_trials)) * 100 if interventional_trials else 0
        print(f"  {intervention_type}: {count} trials ({percentage:.1f}%)")

def demo_phase_analysis():
    """Demonstrate phase analysis for interventional trials"""
    print("\n=== Phase Analysis Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for immunotherapy trials
    print("Searching for immunotherapy trials...")
    trials = api.search_trials(query="immunotherapy", max_results=25)
    
    # Filter for interventional trials
    interventional_trials = processor.filter_interventional_trials(trials)
    print(f"Found {len(interventional_trials)} interventional immunotherapy trials")
    
    # Analyze by phase
    phase_counts = {}
    for trial in interventional_trials:
        if trial.current_phase:
            phases = str(trial.current_phase).split(', ')
            for phase in phases:
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    print(f"\nPhase Distribution:")
    for phase, count in sorted(phase_counts.items()):
        percentage = (count / len(interventional_trials)) * 100 if interventional_trials else 0
        print(f"  {phase}: {count} trials ({percentage:.1f}%)")

def demo_enhanced_export():
    """Demonstrate enhanced export functionality for interventional trials"""
    print("\n=== Enhanced Export Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for cardiovascular trials
    print("Searching for cardiovascular trials...")
    trials = api.search_trials(query="cardiovascular", max_results=15)
    
    # Filter for interventional trials
    interventional_trials = processor.filter_interventional_trials(trials)
    print(f"Found {len(interventional_trials)} interventional cardiovascular trials")
    
    # Export with enhanced fields
    print("Exporting interventional trials with enhanced fields...")
    files = processor.export_interventional_trials(
        trials=interventional_trials,
        format_type="both",
        filename_prefix="cardiovascular_interventional"
    )
    
    print(f"Files created: {files}")
    
    # Create comprehensive summary
    summary = processor.create_interventional_summary_report(trials)
    stats = processor.get_interventional_trial_statistics(trials)
    
    print(f"\nComprehensive Summary:")
    print(f"  Total interventional trials: {summary['total_interventional_trials']}")
    print(f"  Percentage of all trials: {summary['interventional_percentage']}%")
    print(f"  Recruiting trials: {stats['recruiting_trials']}")
    print(f"  Completed trials: {stats['completed_trials']}")
    print(f"  Phase 1 trials: {stats['phase_1_trials']}")
    print(f"  Phase 2 trials: {stats['phase_2_trials']}")
    print(f"  Phase 3 trials: {stats['phase_3_trials']}")

def demo_pharmaceutical_company_analysis():
    """Demonstrate analysis by pharmaceutical companies for interventional trials"""
    print("\n=== Pharmaceutical Company Analysis Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for trials by specific companies
    companies = ["Pfizer", "Merck", "Johnson & Johnson", "Novartis", "Roche"]
    
    all_interventional_trials = []
    company_stats = {}
    
    for company in companies:
        print(f"Searching for trials by {company}...")
        
        trials = api.search_trials(
            query=f"sponsor:{company}",
            max_results=10
        )
        
        # Filter for interventional trials
        interventional_trials = processor.filter_interventional_trials(trials)
        print(f"  Found {len(interventional_trials)} interventional trials")
        
        company_stats[company] = {
            'total_trials': len(trials),
            'interventional_trials': len(interventional_trials),
            'interventional_percentage': (len(interventional_trials) / len(trials)) * 100 if trials else 0
        }
        
        all_interventional_trials.extend(interventional_trials)
    
    print(f"\nCompany Analysis:")
    for company, stats in company_stats.items():
        print(f"  {company}:")
        print(f"    Total trials: {stats['total_trials']}")
        print(f"    Interventional trials: {stats['interventional_trials']}")
        print(f"    Interventional percentage: {stats['interventional_percentage']:.1f}%")
    
    print(f"\nTotal interventional trials across all companies: {len(all_interventional_trials)}")
    
    # Export all interventional trials
    files = processor.export_interventional_trials(
        trials=all_interventional_trials,
        format_type="csv",
        filename_prefix="pharma_interventional_analysis"
    )
    print(f"Files created: {files}")

def demo_status_analysis():
    """Demonstrate analysis by recruitment status for interventional trials"""
    print("\n=== Recruitment Status Analysis Demo ===")
    
    # Initialize components
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor("./demo_data")
    
    # Search for oncology trials
    print("Searching for oncology trials...")
    trials = api.search_trials(query="oncology cancer", max_results=40)
    
    # Filter for interventional trials
    interventional_trials = processor.filter_interventional_trials(trials)
    print(f"Found {len(interventional_trials)} interventional oncology trials")
    
    # Analyze by status
    status_counts = {}
    for trial in interventional_trials:
        status = trial.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\nRecruitment Status Analysis:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(interventional_trials)) * 100 if interventional_trials else 0
        print(f"  {status}: {count} trials ({percentage:.1f}%)")
    
    # Show examples of each status
    print(f"\nExamples by Status:")
    for status in status_counts.keys():
        example_trial = next((t for t in interventional_trials if t.status == status), None)
        if example_trial:
            print(f"  {status}: {example_trial.brief_title}")

def main():
    """Run all interventional trials demonstrations"""
    print("Interventional Clinical Trials Data Scraper - Demonstration")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demo_interventional_trials_search()
        demo_intervention_type_analysis()
        demo_phase_analysis()
        demo_enhanced_export()
        demo_pharmaceutical_company_analysis()
        demo_status_analysis()
        
        print("\n" + "=" * 60)
        print("✅ All interventional trials demonstrations completed successfully!")
        print("\nYou can now use the specialized interventional trials scraper with:")
        print("  python3 interventional_main.py search --query 'cancer treatment' --max-results 100")
        print("  python3 interventional_main.py get-trial NCT12345678")
        print("  python3 interventional_main.py analyze-phases --query 'diabetes'")
        print("  python3 interventional_demo.py")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()

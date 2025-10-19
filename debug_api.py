#!/usr/bin/env python3
"""
Debug script to examine API response structure
"""
import json
from clinical_trials_api import ClinicalTrialsAPI

def debug_api_response():
    """Debug the API response structure"""
    api = ClinicalTrialsAPI()
    
    # Get a single trial
    trials = api.search_trials(query="cancer", max_results=1)
    
    if trials:
        trial = trials[0]
        print("=== Raw API Response Structure ===")
        print(f"NCT ID: {trial.nct_id}")
        print(f"Brief Title: {trial.brief_title}")
        print(f"Study Type: {trial.study_type}")
        print(f"Interventions: {trial.interventions}")
        print(f"Conditions: {trial.conditions}")
        print(f"Sponsors: {trial.sponsors}")
        
        # Check raw data
        if hasattr(trial, 'raw_data') and trial.raw_data:
            print("\n=== Raw Data Structure ===")
            protocol_section = trial.raw_data.get('protocolSection', {})
            print(f"Protocol section keys: {list(protocol_section.keys())}")
            
            interventions_module = protocol_section.get('interventionsModule', {})
            print(f"Interventions module: {interventions_module}")
            
            conditions_module = protocol_section.get('conditionsModule', {})
            print(f"Conditions module: {conditions_module}")
            
            sponsor_module = protocol_section.get('sponsorCollaboratorsModule', {})
            print(f"Sponsor module: {sponsor_module}")

if __name__ == "__main__":
    debug_api_response()

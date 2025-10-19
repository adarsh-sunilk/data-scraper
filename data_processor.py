"""
Data processing and export functionality for clinical trials data
"""
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path

from models import ClinicalTrial
from config import OUTPUT_DIRECTORY, OUTPUT_FORMAT

class DataProcessor:
    """Handles data processing and export operations"""
    
    def __init__(self, output_dir: str = OUTPUT_DIRECTORY):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_trials(self, 
                     trials: List[ClinicalTrial], 
                     format_type: str = OUTPUT_FORMAT,
                     filename_prefix: str = "clinical_trials") -> List[str]:
        """
        Export clinical trials data to specified format(s)
        
        Args:
            trials: List of ClinicalTrial objects
            format_type: Export format ('csv', 'json', or 'both')
            filename_prefix: Prefix for output files
            
        Returns:
            List of created file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        created_files = []
        
        if format_type in ['csv', 'both']:
            csv_file = self._export_to_csv(trials, filename_prefix, timestamp)
            if csv_file:
                created_files.append(csv_file)
        
        if format_type in ['json', 'both']:
            json_file = self._export_to_json(trials, filename_prefix, timestamp)
            if json_file:
                created_files.append(json_file)
        
        return created_files
    
    def _export_to_csv(self, 
                      trials: List[ClinicalTrial], 
                      filename_prefix: str,
                      timestamp: str) -> Optional[str]:
        """Export trials to CSV format"""
        try:
            # Convert trials to list of dictionaries
            data = []
            for trial in trials:
                row = self._trial_to_dict(trial)
                data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename
            filename = f"{filename_prefix}_{timestamp}.csv"
            filepath = self.output_dir / filename
            
            # Export to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            print(f"Exported {len(trials)} trials to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None
    
    def _export_to_json(self, 
                       trials: List[ClinicalTrial], 
                       filename_prefix: str,
                       timestamp: str) -> Optional[str]:
        """Export trials to JSON format"""
        try:
            # Convert trials to list of dictionaries
            data = []
            for trial in trials:
                row = self._trial_to_dict(trial)
                data.append(row)
            
            # Generate filename
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            # Export to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"Exported {len(trials)} trials to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return None
    
    def _trial_to_dict(self, trial: ClinicalTrial) -> Dict[str, Any]:
        """Convert ClinicalTrial object to dictionary for export"""
        return {
            'NCT ID': trial.nct_id,
            'Brief Title': trial.brief_title,
            'Official Title': trial.official_title,
            'Status': trial.status,
            'Current Phase': trial.current_phase,
            'Start Date': trial.start_date.isoformat() if trial.start_date else None,
            'Completion Date': trial.completion_date.isoformat() if trial.completion_date else None,
            'Primary Completion Date': trial.primary_completion_date.isoformat() if trial.primary_completion_date else None,
            'Conditions': '; '.join([c.name for c in trial.conditions]),
            'Interventions': '; '.join([f"{i.name} ({i.type})" for i in trial.interventions]),
            'Sponsors': '; '.join([s.name for s in trial.sponsors]),
            'Locations': '; '.join([f"{l.facility}, {l.city}, {l.country}" for l in trial.locations]),
            'Study Type': trial.study_type,
            'Enrollment': trial.enrollment,
            'Study Population': trial.study_population
        }
    
    def create_summary_report(self, trials: List[ClinicalTrial]) -> Dict[str, Any]:
        """Create a summary report of the collected trials"""
        if not trials:
            return {"error": "No trials to summarize"}
        
        # Basic statistics
        total_trials = len(trials)
        
        # Status distribution
        status_counts = {}
        for trial in trials:
            status = trial.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Phase distribution
        phase_counts = {}
        for trial in trials:
            if trial.current_phase:
                phases = trial.current_phase.split(', ')
                for phase in phases:
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Sponsor distribution
        sponsor_counts = {}
        for trial in trials:
            for sponsor in trial.sponsors:
                sponsor_name = sponsor.name
                sponsor_counts[sponsor_name] = sponsor_counts.get(sponsor_name, 0) + 1
        
        # Date range
        start_dates = [trial.start_date for trial in trials if trial.start_date]
        completion_dates = [trial.completion_date for trial in trials if trial.completion_date]
        
        summary = {
            'total_trials': total_trials,
            'status_distribution': status_counts,
            'phase_distribution': phase_counts,
            'top_sponsors': dict(sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'date_range': {
                'earliest_start': min(start_dates).isoformat() if start_dates else None,
                'latest_start': max(start_dates).isoformat() if start_dates else None,
                'earliest_completion': min(completion_dates).isoformat() if completion_dates else None,
                'latest_completion': max(completion_dates).isoformat() if completion_dates else None
            }
        }
        
        return summary

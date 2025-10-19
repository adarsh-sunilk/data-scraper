"""
Specialized data processor for interventional clinical trials
Focuses specifically on clinical trials (interventional studies) as opposed to observational studies
"""
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path

from models import ClinicalTrial, SearchFilters
from config import OUTPUT_DIRECTORY

class InterventionalTrialsProcessor:
    """Specialized processor for interventional clinical trials data"""
    
    def __init__(self, output_dir: str = OUTPUT_DIRECTORY):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectory for interventional trials
        self.interventional_dir = self.output_dir / "interventional_trials"
        self.interventional_dir.mkdir(exist_ok=True)
    
    def filter_interventional_trials(self, trials: List[ClinicalTrial]) -> List[ClinicalTrial]:
        """
        Filter trials to include only interventional studies
        
        Args:
            trials: List of all clinical trials
            
        Returns:
            List of interventional trials only
        """
        interventional_trials = []
        
        for trial in trials:
            # Check if trial is interventional
            if self._is_interventional_trial(trial):
                interventional_trials.append(trial)
        
        return interventional_trials
    
    def _is_interventional_trial(self, trial: ClinicalTrial) -> bool:
        """
        Determine if a trial is interventional based on various criteria
        
        Args:
            trial: ClinicalTrial object
            
        Returns:
            True if trial is interventional, False otherwise
        """
        # Check study type
        if trial.study_type and "INTERVENTIONAL" in trial.study_type.upper():
            return True
        
        # Check if trial has interventions
        if trial.interventions and len(trial.interventions) > 0:
            return True
        
        # Check if trial has phases (interventional trials typically have phases)
        if trial.current_phase and trial.current_phase != "NA":
            return True
        
        # Check for clinical trial keywords in title
        title_keywords = [
            "clinical trial", "intervention", "treatment", "therapy", 
            "drug", "medication", "device", "procedure", "surgery",
            "randomized", "controlled", "phase", "dose", "efficacy"
        ]
        
        title_text = (trial.brief_title + " " + trial.official_title).lower()
        if any(keyword in title_text for keyword in title_keywords):
            return True
        
        return False
    
    def export_interventional_trials(self, 
                                   trials: List[ClinicalTrial], 
                                   format_type: str = "csv",
                                   filename_prefix: str = "interventional_trials") -> List[str]:
        """
        Export interventional trials data to specified format(s)
        
        Args:
            trials: List of ClinicalTrial objects
            format_type: Export format ('csv', 'json', or 'both')
            filename_prefix: Prefix for output files
            
        Returns:
            List of created file paths
        """
        # Filter for interventional trials only
        interventional_trials = self.filter_interventional_trials(trials)
        
        if not interventional_trials:
            print("No interventional trials found in the provided data")
            return []
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        created_files = []
        
        if format_type in ['csv', 'both']:
            csv_file = self._export_to_csv(interventional_trials, filename_prefix, timestamp)
            if csv_file:
                created_files.append(csv_file)
        
        if format_type in ['json', 'both']:
            json_file = self._export_to_json(interventional_trials, filename_prefix, timestamp)
            if json_file:
                created_files.append(json_file)
        
        return created_files
    
    def _export_to_csv(self, 
                      trials: List[ClinicalTrial], 
                      filename_prefix: str,
                      timestamp: str) -> Optional[str]:
        """Export interventional trials to CSV format with enhanced fields"""
        try:
            # Convert trials to list of dictionaries with enhanced interventional trial fields
            data = []
            for trial in trials:
                row = self._trial_to_interventional_dict(trial)
                data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename
            filename = f"{filename_prefix}_{timestamp}.csv"
            filepath = self.interventional_dir / filename
            
            # Export to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            print(f"Exported {len(trials)} interventional trials to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error exporting interventional trials to CSV: {e}")
            return None
    
    def _export_to_json(self, 
                       trials: List[ClinicalTrial], 
                       filename_prefix: str,
                       timestamp: str) -> Optional[str]:
        """Export interventional trials to JSON format"""
        try:
            # Convert trials to list of dictionaries
            data = []
            for trial in trials:
                row = self._trial_to_interventional_dict(trial)
                data.append(row)
            
            # Generate filename
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = self.interventional_dir / filename
            
            # Export to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"Exported {len(trials)} interventional trials to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error exporting interventional trials to JSON: {e}")
            return None
    
    def _trial_to_interventional_dict(self, trial: ClinicalTrial) -> Dict[str, Any]:
        """Convert ClinicalTrial object to dictionary with enhanced interventional trial fields"""
        return {
            # Basic Information
            'NCT ID': trial.nct_id,
            'Brief Title': trial.brief_title,
            'Official Title': trial.official_title,
            'Study Type': trial.study_type,
            
            # Trial Status and Phase Information
            'Recruitment Status': trial.status,
            'Current Phase': trial.current_phase,
            'Phase Details': self._extract_phase_details(trial),
            
            # Important Dates
            'Start Date': trial.start_date.isoformat() if trial.start_date else None,
            'Completion Date': trial.completion_date.isoformat() if trial.completion_date else None,
            'Primary Completion Date': trial.primary_completion_date.isoformat() if trial.primary_completion_date else None,
            
            # Medical Information
            'Conditions Treated': '; '.join([c.name for c in trial.conditions]),
            'Interventions': '; '.join([f"{i.name} ({i.type})" for i in trial.interventions]),
            'Intervention Types': '; '.join([i.type for i in trial.interventions]),
            'Intervention Names': '; '.join([i.name for i in trial.interventions]),
            
            # Sponsor and Organization Information
            'Lead Sponsor': trial.sponsors[0].name if trial.sponsors else None,
            'All Sponsors': '; '.join([s.name for s in trial.sponsors]),
            'Sponsor Types': '; '.join([s.type for s in trial.sponsors]),
            
            # Study Locations
            'Study Locations': '; '.join([f"{l.facility}, {l.city}, {l.country}" for l in trial.locations]),
            'Countries': '; '.join(list(set([l.country for l in trial.locations]))),
            'Cities': '; '.join(list(set([l.city for l in trial.locations]))),
            
            # Study Design Information
            'Enrollment': trial.enrollment,
            'Study Population': trial.study_population,
            'Is Interventional': self._is_interventional_trial(trial),
            
            # Additional Interventional Trial Specific Fields
            'Has Drug Intervention': self._has_drug_intervention(trial),
            'Has Device Intervention': self._has_device_intervention(trial),
            'Has Procedure Intervention': self._has_procedure_intervention(trial),
            'Has Behavioral Intervention': self._has_behavioral_intervention(trial),
            'Has Biological Intervention': self._has_biological_intervention(trial),
            'Has Radiation Intervention': self._has_radiation_intervention(trial),
            
            # Phase-specific information
            'Is Phase 0': 'PHASE0' in str(trial.current_phase) if trial.current_phase else False,
            'Is Phase 1': 'PHASE1' in str(trial.current_phase) if trial.current_phase else False,
            'Is Phase 2': 'PHASE2' in str(trial.current_phase) if trial.current_phase else False,
            'Is Phase 3': 'PHASE3' in str(trial.current_phase) if trial.current_phase else False,
            'Is Phase 4': 'PHASE4' in str(trial.current_phase) if trial.current_phase else False,
            
            # Status-specific information
            'Is Recruiting': trial.status == 'RECRUITING',
            'Is Completed': trial.status == 'COMPLETED',
            'Is Terminated': trial.status == 'TERMINATED',
            'Is Suspended': trial.status == 'SUSPENDED',
            'Is Not Yet Recruiting': trial.status == 'NOT_YET_RECRUITING',
            'Is Active Not Recruiting': trial.status == 'ACTIVE_NOT_RECRUITING',
        }
    
    def _extract_phase_details(self, trial: ClinicalTrial) -> str:
        """Extract detailed phase information"""
        if not trial.current_phase:
            return "Not specified"
        
        phases = []
        if 'PHASE0' in str(trial.current_phase):
            phases.append("Phase 0 (Exploratory)")
        if 'PHASE1' in str(trial.current_phase):
            phases.append("Phase 1 (Safety)")
        if 'PHASE2' in str(trial.current_phase):
            phases.append("Phase 2 (Efficacy)")
        if 'PHASE3' in str(trial.current_phase):
            phases.append("Phase 3 (Confirmation)")
        if 'PHASE4' in str(trial.current_phase):
            phases.append("Phase 4 (Post-marketing)")
        
        return "; ".join(phases) if phases else str(trial.current_phase)
    
    def _has_drug_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has drug interventions"""
        drug_keywords = ['drug', 'medication', 'pharmaceutical', 'compound', 'agent', 'therapy']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in drug_keywords):
                return True
        return False
    
    def _has_device_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has device interventions"""
        device_keywords = ['device', 'equipment', 'instrument', 'apparatus', 'tool']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in device_keywords):
                return True
        return False
    
    def _has_procedure_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has procedure interventions"""
        procedure_keywords = ['procedure', 'surgery', 'surgical', 'operation', 'technique']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in procedure_keywords):
                return True
        return False
    
    def _has_behavioral_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has behavioral interventions"""
        behavioral_keywords = ['behavioral', 'behavior', 'psychological', 'psychotherapy', 'counseling', 'education']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in behavioral_keywords):
                return True
        return False
    
    def _has_biological_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has biological interventions"""
        biological_keywords = ['biological', 'biologic', 'vaccine', 'immunotherapy', 'cell therapy', 'gene therapy']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in biological_keywords):
                return True
        return False
    
    def _has_radiation_intervention(self, trial: ClinicalTrial) -> bool:
        """Check if trial has radiation interventions"""
        radiation_keywords = ['radiation', 'radiotherapy', 'irradiation', 'radioactive']
        for intervention in trial.interventions:
            if any(keyword in intervention.type.lower() for keyword in radiation_keywords):
                return True
        return False
    
    def create_interventional_summary_report(self, trials: List[ClinicalTrial]) -> Dict[str, Any]:
        """Create a comprehensive summary report for interventional trials"""
        interventional_trials = self.filter_interventional_trials(trials)
        
        if not interventional_trials:
            return {"error": "No interventional trials to summarize"}
        
        # Basic statistics
        total_trials = len(interventional_trials)
        
        # Status distribution
        status_counts = {}
        for trial in interventional_trials:
            status = trial.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Phase distribution
        phase_counts = {}
        for trial in interventional_trials:
            if trial.current_phase:
                phases = str(trial.current_phase).split(', ')
                for phase in phases:
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Intervention type distribution
        intervention_type_counts = {}
        for trial in interventional_trials:
            for intervention in trial.interventions:
                intervention_type = intervention.type
                intervention_type_counts[intervention_type] = intervention_type_counts.get(intervention_type, 0) + 1
        
        # Sponsor distribution
        sponsor_counts = {}
        for trial in interventional_trials:
            for sponsor in trial.sponsors:
                sponsor_name = sponsor.name
                sponsor_counts[sponsor_name] = sponsor_counts.get(sponsor_name, 0) + 1
        
        # Intervention category analysis
        intervention_categories = {
            'Drug Interventions': sum(1 for trial in interventional_trials if self._has_drug_intervention(trial)),
            'Device Interventions': sum(1 for trial in interventional_trials if self._has_device_intervention(trial)),
            'Procedure Interventions': sum(1 for trial in interventional_trials if self._has_procedure_intervention(trial)),
            'Behavioral Interventions': sum(1 for trial in interventional_trials if self._has_behavioral_intervention(trial)),
            'Biological Interventions': sum(1 for trial in interventional_trials if self._has_biological_intervention(trial)),
            'Radiation Interventions': sum(1 for trial in interventional_trials if self._has_radiation_intervention(trial)),
        }
        
        # Date range
        start_dates = [trial.start_date for trial in interventional_trials if trial.start_date]
        completion_dates = [trial.completion_date for trial in interventional_trials if trial.completion_date]
        
        summary = {
            'total_interventional_trials': total_trials,
            'total_all_trials': len(trials),
            'interventional_percentage': round((total_trials / len(trials)) * 100, 2) if trials else 0,
            'status_distribution': status_counts,
            'phase_distribution': phase_counts,
            'intervention_type_distribution': intervention_type_counts,
            'intervention_categories': intervention_categories,
            'top_sponsors': dict(sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'date_range': {
                'earliest_start': min(start_dates).isoformat() if start_dates else None,
                'latest_start': max(start_dates).isoformat() if start_dates else None,
                'earliest_completion': min(completion_dates).isoformat() if completion_dates else None,
                'latest_completion': max(completion_dates).isoformat() if completion_dates else None
            }
        }
        
        return summary
    
    def get_interventional_trial_statistics(self, trials: List[ClinicalTrial]) -> Dict[str, Any]:
        """Get detailed statistics for interventional trials"""
        interventional_trials = self.filter_interventional_trials(trials)
        
        if not interventional_trials:
            return {"error": "No interventional trials found"}
        
        stats = {
            'total_interventional_trials': len(interventional_trials),
            'recruiting_trials': len([t for t in interventional_trials if t.status == 'RECRUITING']),
            'completed_trials': len([t for t in interventional_trials if t.status == 'COMPLETED']),
            'phase_1_trials': len([t for t in interventional_trials if 'PHASE1' in str(t.current_phase)]),
            'phase_2_trials': len([t for t in interventional_trials if 'PHASE2' in str(t.current_phase)]),
            'phase_3_trials': len([t for t in interventional_trials if 'PHASE3' in str(t.current_phase)]),
            'phase_4_trials': len([t for t in interventional_trials if 'PHASE4' in str(t.current_phase)]),
            'drug_trials': len([t for t in interventional_trials if self._has_drug_intervention(t)]),
            'device_trials': len([t for t in interventional_trials if self._has_device_intervention(t)]),
            'behavioral_trials': len([t for t in interventional_trials if self._has_behavioral_intervention(t)]),
        }
        
        return stats

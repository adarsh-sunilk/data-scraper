"""
ClinicalTrials.gov API client for retrieving clinical trial data
"""
import requests
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import logging

from models import ClinicalTrial, SearchFilters
from config import CLINICAL_TRIALS_API_BASE_URL, MAX_RESULTS_PER_REQUEST, REQUEST_DELAY

logger = logging.getLogger(__name__)


class ClinicalTrialsAPI:
    """Client for interacting with ClinicalTrials.gov API v2"""
    
    def __init__(self, base_url: str = CLINICAL_TRIALS_API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClinicalTrials-DataScraper/1.0 (Educational Purpose)',
            'Accept': 'application/json'
        })
    
    def search_trials(self, 
                     query: str = "",
                     filters: Optional[SearchFilters] = None,
                     max_results: int = 1000) -> List[ClinicalTrial]:
        """
        Search for clinical trials based on query and filters
        
        Args:
            query: Search query string
            filters: Search filters to apply
            max_results: Maximum number of results to return
            
        Returns:
            List of ClinicalTrial objects
        """
        all_trials = []
        offset = 0
        
        while len(all_trials) < max_results:
            # Build search parameters
            params = self._build_search_params(query, filters, offset)
            
            try:
                # Make API request
                response = self._make_request(params)
                if not response:
                    break
                
                # Parse response
                trials = self._parse_response(response)
                if not trials:
                    break
                
                all_trials.extend(trials)
                offset += len(trials)
                
                # Respect API rate limits
                time.sleep(REQUEST_DELAY)
                
                logger.info(f"Retrieved {len(trials)} trials (total: {len(all_trials)})")
                
            except Exception as e:
                logger.error(f"Error retrieving trials: {e}")
                break
        
        return all_trials[:max_results]
    
    def get_trial_details(self, nct_id: str) -> Optional[ClinicalTrial]:
        """
        Get detailed information for a specific trial by NCT ID
        
        Args:
            nct_id: NCT identifier (e.g., "NCT12345678")
            
        Returns:
            ClinicalTrial object or None if not found
        """
        try:
            url = f"{self.base_url}/{nct_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_single_trial(data)
            
        except Exception as e:
            logger.error(f"Error retrieving trial {nct_id}: {e}")
            return None
    
    def _build_search_params(self, 
                           query: str, 
                           filters: Optional[SearchFilters], 
                           offset: int) -> Dict[str, Any]:
        """Build search parameters for API request"""
        params = {
            'query.term': query,
            'format': 'json',
            'pageSize': min(MAX_RESULTS_PER_REQUEST, 1000)
        }
        
        # Add pageToken only if offset > 0
        if offset > 0:
            params['pageToken'] = str(offset)
        
        return params
    
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request with error handling"""
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _parse_response(self, response: Dict[str, Any]) -> List[ClinicalTrial]:
        """Parse API response and convert to ClinicalTrial objects"""
        trials = []
        
        try:
            studies = response.get('studies', [])
            for study in studies:
                trial = self._parse_single_trial(study)
                if trial:
                    trials.append(trial)
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        return trials
    
    def _parse_single_trial(self, study_data: Dict[str, Any]) -> Optional[ClinicalTrial]:
        """Parse a single study from API response"""
        try:
            protocol_section = study_data.get('protocolSection', {})
            identification_module = protocol_section.get('identificationModule', {})
            status_module = protocol_section.get('statusModule', {})
            design_module = protocol_section.get('designModule', {})
            conditions_module = protocol_section.get('conditionsModule', {})
            interventions_module = protocol_section.get('interventionsModule', {})
            sponsor_collaborators_module = protocol_section.get('sponsorCollaboratorsModule', {})
            locations_module = protocol_section.get('locationsModule', {})
            
            # Extract basic information
            nct_id = identification_module.get('nctId', '')
            brief_title = identification_module.get('briefTitle', '')
            official_title = identification_module.get('officialTitle', '')
            
            # Extract status and phase information
            status = status_module.get('overallStatus', '')
            phases = design_module.get('phases', [])
            current_phase = ', '.join(phases) if phases else None
            
            # Extract dates
            start_date = self._parse_date(status_module.get('startDateStruct', {}).get('date'))
            completion_date = self._parse_date(status_module.get('completionDateStruct', {}).get('date'))
            primary_completion_date = self._parse_date(status_module.get('primaryCompletionDateStruct', {}).get('date'))
            
            # Extract conditions
            conditions = []
            for condition in conditions_module.get('conditions', []):
                conditions.append({
                    'name': condition,
                    'description': None
                })
            
            # Extract interventions
            interventions = []
            for intervention in interventions_module.get('interventions', []):
                interventions.append({
                    'name': intervention.get('name', ''),
                    'type': intervention.get('type', ''),
                    'description': intervention.get('description')
                })
            
            # Extract sponsors
            sponsors = []
            lead_sponsor = sponsor_collaborators_module.get('leadSponsor', {})
            if lead_sponsor:
                sponsors.append({
                    'name': lead_sponsor.get('name', ''),
                    'type': lead_sponsor.get('class', '')
                })
            
            # Extract locations
            locations = []
            for location in locations_module.get('locations', []):
                facility = location.get('facility', {})
                locations.append({
                    'facility': facility.get('name', ''),
                    'city': facility.get('city', ''),
                    'state': facility.get('state', ''),
                    'country': facility.get('country', '')
                })
            
            # Create ClinicalTrial object
            trial = ClinicalTrial(
                nct_id=nct_id,
                brief_title=brief_title,
                official_title=official_title,
                status=status,
                current_phase=current_phase,
                start_date=start_date,
                completion_date=completion_date,
                primary_completion_date=primary_completion_date,
                conditions=conditions,
                interventions=interventions,
                sponsors=sponsors,
                locations=locations,
                raw_data=study_data
            )
            
            return trial
            
        except Exception as e:
            logger.error(f"Error parsing trial data: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle various date formats from the API
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None

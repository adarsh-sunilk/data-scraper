"""
Data models for clinical trials information
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PhaseInfo(BaseModel):
    """Information about a specific trial phase"""
    phase: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Intervention(BaseModel):
    """Intervention or treatment information"""
    name: str
    type: str
    description: Optional[str] = None


class Condition(BaseModel):
    """Medical condition being studied"""
    name: str
    description: Optional[str] = None


class Sponsor(BaseModel):
    """Study sponsor information"""
    name: str
    type: str  # e.g., "INDUSTRY", "NIH", "OTHER"


class Location(BaseModel):
    """Study location information"""
    facility: str
    city: str
    state: Optional[str] = None
    country: str


class ClinicalTrial(BaseModel):
    """Complete clinical trial information"""
    nct_id: str = Field(..., description="NCT ID (unique identifier)")
    brief_title: str
    official_title: str
    status: str = Field(..., description="Recruitment status")
    
    # Phase information
    phases: List[PhaseInfo] = Field(default_factory=list)
    current_phase: Optional[str] = None
    
    # Dates
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    primary_completion_date: Optional[datetime] = None
    
    # Study details
    conditions: List[Condition] = Field(default_factory=list)
    interventions: List[Intervention] = Field(default_factory=list)
    sponsors: List[Sponsor] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    
    # Additional metadata
    study_type: str = "INTERVENTIONAL"
    enrollment: Optional[int] = None
    study_population: Optional[str] = None
    
    # Raw data for debugging
    raw_data: Optional[Dict[str, Any]] = None


class SearchFilters(BaseModel):
    """Filters for searching clinical trials"""
    study_type: str = "INTERVENTIONAL"
    phases: Optional[List[str]] = None
    status: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    interventions: Optional[List[str]] = None
    sponsors: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None

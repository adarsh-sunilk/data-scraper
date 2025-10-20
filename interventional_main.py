#!/usr/bin/env python3
"""
Specialized CLI for interventional clinical trials data extraction
Focuses specifically on clinical trials (interventional studies)
"""
import click
import logging
from typing import List, Optional
from datetime import datetime

from clinical_trials_api import ClinicalTrialsAPI
from interventional_trials_processor import InterventionalTrialsProcessor
from models import SearchFilters
from config import DEFAULT_SEARCH_TERMS
from phase_dates_processor import PhaseDatesProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Interventional Clinical Trials Data Scraper - Focus on clinical trials only"""
    pass

@cli.command()
@click.option('--query', '-q', default='', help='Search query for interventional clinical trials')
@click.option('--max-results', '-m', default=1000, help='Maximum number of results to retrieve')
@click.option('--phases', '-p', multiple=True, help='Filter by trial phases (e.g., PHASE1, PHASE2)')
@click.option('--status', '-s', multiple=True, help='Filter by recruitment status')
@click.option('--conditions', '-c', multiple=True, help='Filter by medical conditions')
@click.option('--sponsors', help='Filter by sponsor names (comma-separated)')
@click.option('--countries', help='Filter by countries (comma-separated)')
@click.option('--intervention-type', help='Filter by intervention type (drug, device, procedure, behavioral, biological, radiation)')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'json', 'both']), 
              default='csv',
              help='Output format for exported data')
@click.option('--output-dir', '-o', default='./data', help='Output directory for exported files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def search(query, max_results, phases, status, conditions, sponsors, countries, 
         intervention_type, output_format, output_dir, verbose):
    """
    Search for interventional clinical trials
    
    This command specifically focuses on interventional studies (clinical trials)
    and filters out observational studies.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize API client and specialized processor
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor(output_dir)
    
    # Build search filters with interventional focus
    filters = SearchFilters(
        study_type="INTERVENTIONAL",  # Force interventional studies
        phases=list(phases) if phases else None,
        status=list(status) if status else None,
        conditions=list(conditions) if conditions else None,
        sponsors=sponsors.split(',') if sponsors else None,
        countries=countries.split(',') if countries else None
    )
    
    # Use default search terms if no query provided
    if not query:
        query = ' '.join(DEFAULT_SEARCH_TERMS)
        logger.info(f"Using default search terms: {query}")
    
    logger.info(f"Starting interventional trials search with query: '{query}'")
    logger.info(f"Max results: {max_results}")
    logger.info(f"Filters: {filters}")
    
    try:
        # Search for trials
        logger.info("Searching for clinical trials...")
        trials = api.search_trials(
            query=query,
            filters=filters,
            max_results=max_results
        )
        
        if not trials:
            logger.warning("No trials found matching the search criteria")
            return
        
        logger.info(f"Found {len(trials)} total trials")
        
        # Filter for interventional trials specifically
        interventional_trials = processor.filter_interventional_trials(trials)
        logger.info(f"Found {len(interventional_trials)} interventional trials")
        
        if not interventional_trials:
            logger.warning("No interventional trials found in the results")
            return
        
        # Apply additional intervention type filter if specified
        if intervention_type:
            interventional_trials = _filter_by_intervention_type(interventional_trials, intervention_type, processor)
            logger.info(f"After intervention type filtering: {len(interventional_trials)} trials")
        
        # Export data
        logger.info(f"Exporting interventional trials data in {output_format} format...")
        created_files = processor.export_interventional_trials(
            trials=interventional_trials,
            format_type=output_format,
            filename_prefix="interventional_trials"
        )
        
        # Create comprehensive summary report
        summary = processor.create_interventional_summary_report(trials)
        stats = processor.get_interventional_trial_statistics(trials)
        
        # Display results
        click.echo(f"\n✅ Successfully processed {len(interventional_trials)} interventional clinical trials")
        click.echo(f"📁 Files created: {', '.join(created_files)}")
        
        # Display comprehensive summary
        click.echo(f"\n📊 Interventional Trials Summary:")
        click.echo(f"   Total interventional trials: {summary['total_interventional_trials']}")
        click.echo(f"   Percentage of all trials: {summary['interventional_percentage']}%")
        click.echo(f"   Status distribution: {summary['status_distribution']}")
        click.echo(f"   Phase distribution: {summary['phase_distribution']}")
        
        if summary['intervention_categories']:
            click.echo(f"   Intervention categories:")
            for category, count in summary['intervention_categories'].items():
                if count > 0:
                    click.echo(f"     - {category}: {count} trials")
        
        if summary['top_sponsors']:
            click.echo(f"   Top sponsors:")
            for sponsor, count in list(summary['top_sponsors'].items())[:5]:
                click.echo(f"     - {sponsor}: {count} trials")
        
        # Display detailed statistics
        click.echo(f"\n📈 Detailed Statistics:")
        click.echo(f"   Recruiting trials: {stats['recruiting_trials']}")
        click.echo(f"   Completed trials: {stats['completed_trials']}")
        click.echo(f"   Phase 1 trials: {stats['phase_1_trials']}")
        click.echo(f"   Phase 2 trials: {stats['phase_2_trials']}")
        click.echo(f"   Phase 3 trials: {stats['phase_3_trials']}")
        click.echo(f"   Drug trials: {stats['drug_trials']}")
        click.echo(f"   Device trials: {stats['device_trials']}")
        click.echo(f"   Behavioral trials: {stats['behavioral_trials']}")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('nct_id')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'json', 'both']), 
              default='json',
              help='Output format for exported data')
@click.option('--output-dir', '-o', default='./data', help='Output directory for exported files')
def get_trial(nct_id, output_format, output_dir):
    """
    Get detailed information for a specific interventional clinical trial by NCT ID
    
    Example: python3 interventional_main.py get-trial NCT12345678
    """
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor(output_dir)
    
    logger.info(f"Retrieving interventional trial details for {nct_id}")
    
    try:
        trial = api.get_trial_details(nct_id)
        
        if not trial:
            click.echo(f"❌ Trial {nct_id} not found", err=True)
            return
        
        # Check if it's an interventional trial
        if not processor._is_interventional_trial(trial):
            click.echo(f"⚠️  Trial {nct_id} is not an interventional study", err=True)
            click.echo(f"   Study type: {trial.study_type}")
            click.echo(f"   This tool focuses on interventional clinical trials only")
            return
        
        # Export single trial
        created_files = processor.export_interventional_trials(
            trials=[trial],
            format_type=output_format,
            filename_prefix=f"interventional_trial_{nct_id}"
        )
        
        click.echo(f"✅ Retrieved interventional trial: {trial.brief_title}")
        click.echo(f"   Study type: {trial.study_type}")
        click.echo(f"   Phase: {trial.current_phase}")
        click.echo(f"   Status: {trial.status}")
        click.echo(f"   Interventions: {', '.join([i.name for i in trial.interventions])}")
        click.echo(f"📁 Files created: {', '.join(created_files)}")
        
    except Exception as e:
        logger.error(f"Error retrieving trial {nct_id}: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--query', '-q', default='', help='Search query for interventional clinical trials')
@click.option('--max-results', '-m', default=100, help='Maximum number of results to retrieve')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'json', 'both']), 
              default='csv',
              help='Output format for exported data')
@click.option('--output-dir', '-o', default='./data', help='Output directory for exported files')
def analyze_phases(query, max_results, output_format, output_dir):
    """
    Analyze interventional trials by phase distribution
    
    This command provides detailed analysis of clinical trial phases
    """
    if not query:
        query = ' '.join(DEFAULT_SEARCH_TERMS)
    
    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor(output_dir)
    
    logger.info(f"Analyzing interventional trial phases for query: '{query}'")
    
    try:
        # Search for trials
        trials = api.search_trials(
            query=query,
            filters=SearchFilters(study_type="INTERVENTIONAL"),
            max_results=max_results
        )
        
        # Filter for interventional trials
        interventional_trials = processor.filter_interventional_trials(trials)
        
        if not interventional_trials:
            click.echo("No interventional trials found")
            return
        
        # Create phase analysis
        phase_analysis = _analyze_trial_phases(interventional_trials)
        
        # Export phase analysis
        created_files = processor.export_interventional_trials(
            trials=interventional_trials,
            format_type=output_format,
            filename_prefix="phase_analysis"
        )
        
        click.echo(f"\n📊 Phase Analysis Results:")
        click.echo(f"   Total interventional trials analyzed: {len(interventional_trials)}")
        
        for phase, data in phase_analysis.items():
            click.echo(f"\n   {phase}:")
            click.echo(f"     Count: {data['count']}")
            click.echo(f"     Percentage: {data['percentage']:.1f}%")
            click.echo(f"     Common conditions: {', '.join(data['top_conditions'][:3])}")
            click.echo(f"     Common sponsors: {', '.join(data['top_sponsors'][:3])}")
        
        click.echo(f"\n📁 Files created: {', '.join(created_files)}")
        
    except Exception as e:
        logger.error(f"Error during phase analysis: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--query', '-q', default='', help='Search query for interventional clinical trials')
@click.option('--max-results', '-m', default=200, help='Maximum number of results to retrieve')
@click.option('--output-dir', '-o', default='./data', help='Output directory for exported files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def export_phase_dates(query, max_results, output_dir, verbose):
    """
    Export per-product Phase 1/3 start/end dates and success flags, including company and disorders.
    Columns:
      Company, Product, Disorder/Condition, NCT ID,
      Phase1 Start, Phase1 End, Phase1 Success,
      Phase3 Start, Phase3 End, Phase3 Success
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    api = ClinicalTrialsAPI()
    processor = InterventionalTrialsProcessor(output_dir)
    phase_exporter = PhaseDatesProcessor(output_dir)

    # default query
    if not query:
        query = ' '.join(DEFAULT_SEARCH_TERMS)

    logger.info(f"Exporting phase dates for interventional trials with query: '{query}'")

    try:
        trials = api.search_trials(query=query, filters=SearchFilters(study_type="INTERVENTIONAL"), max_results=max_results)
        interventional_trials = processor.filter_interventional_trials(trials)
        if not interventional_trials:
            click.echo("No interventional trials found for the given query")
            return

        out_file = phase_exporter.export_phase_dates(interventional_trials, filename_prefix="phase_dates")
        click.echo(f"✅ Phase dates exported: {out_file}")

    except Exception as e:
        logger.error(f"Error exporting phase dates: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


def _filter_by_intervention_type(trials: List, intervention_type: str, processor: InterventionalTrialsProcessor) -> List:
    """Filter trials by specific intervention type"""
    filtered_trials = []
    
    for trial in trials:
        if intervention_type.lower() == 'drug' and processor._has_drug_intervention(trial):
            filtered_trials.append(trial)
        elif intervention_type.lower() == 'device' and processor._has_device_intervention(trial):
            filtered_trials.append(trial)
        elif intervention_type.lower() == 'procedure' and processor._has_procedure_intervention(trial):
            filtered_trials.append(trial)
        elif intervention_type.lower() == 'behavioral' and processor._has_behavioral_intervention(trial):
            filtered_trials.append(trial)
        elif intervention_type.lower() == 'biological' and processor._has_biological_intervention(trial):
            filtered_trials.append(trial)
        elif intervention_type.lower() == 'radiation' and processor._has_radiation_intervention(trial):
            filtered_trials.append(trial)
    
    return filtered_trials


def _analyze_trial_phases(trials: List) -> dict:
    """Analyze trials by phase distribution"""
    phase_data = {}
    
    for trial in trials:
        if trial.current_phase:
            phases = str(trial.current_phase).split(', ')
            for phase in phases:
                if phase not in phase_data:
                    phase_data[phase] = {
                        'count': 0,
                        'trials': [],
                        'conditions': [],
                        'sponsors': []
                    }
                
                phase_data[phase]['count'] += 1
                phase_data[phase]['trials'].append(trial)
                phase_data[phase]['conditions'].extend([c.name for c in trial.conditions])
                phase_data[phase]['sponsors'].extend([s.name for s in trial.sponsors])
    
    # Calculate percentages and top items
    total_trials = len(trials)
    for phase, data in phase_data.items():
        data['percentage'] = (data['count'] / total_trials) * 100
        
        # Get top conditions
        condition_counts = {}
        for condition in data['conditions']:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        data['top_conditions'] = sorted(condition_counts.keys(), key=lambda x: condition_counts[x], reverse=True)
        
        # Get top sponsors
        sponsor_counts = {}
        for sponsor in data['sponsors']:
            sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1
        data['top_sponsors'] = sorted(sponsor_counts.keys(), key=lambda x: sponsor_counts[x], reverse=True)
    
    return phase_data


if __name__ == '__main__':
    cli()

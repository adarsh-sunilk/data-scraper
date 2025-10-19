"""
Main script for Clinical Trials Data Scraper
"""
import click
import logging
from typing import List, Optional
from datetime import datetime

from clinical_trials_api import ClinicalTrialsAPI
from data_processor import DataProcessor
from models import SearchFilters
from config import DEFAULT_SEARCH_TERMS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Clinical Trials Data Scraper - Retrieve clinical trial data from ClinicalTrials.gov"""
    pass

@cli.command()
@click.option('--query', '-q', default='', help='Search query for clinical trials')
@click.option('--max-results', '-m', default=1000, help='Maximum number of results to retrieve')
@click.option('--phases', '-p', multiple=True, help='Filter by trial phases (e.g., PHASE1, PHASE2)')
@click.option('--status', '-s', multiple=True, help='Filter by recruitment status')
@click.option('--conditions', '-c', multiple=True, help='Filter by medical conditions')
@click.option('--sponsors', help='Filter by sponsor names (comma-separated)')
@click.option('--countries', help='Filter by countries (comma-separated)')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'json', 'both']), 
              default='csv',
              help='Output format for exported data')
@click.option('--output-dir', '-o', default='./data', help='Output directory for exported files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def search(query, max_results, phases, status, conditions, sponsors, countries, 
         output_format, output_dir, verbose):
    """
    Clinical Trials Data Scraper
    
    Retrieves clinical trial data from ClinicalTrials.gov API and exports it
    in the specified format.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize API client and data processor
    api = ClinicalTrialsAPI()
    processor = DataProcessor(output_dir)
    
    # Build search filters
    filters = SearchFilters(
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
    
    logger.info(f"Starting search with query: '{query}'")
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
        
        logger.info(f"Found {len(trials)} clinical trials")
        
        # Export data
        logger.info(f"Exporting data in {output_format} format...")
        created_files = processor.export_trials(
            trials=trials,
            format_type=output_format,
            filename_prefix="clinical_trials"
        )
        
        # Create summary report
        summary = processor.create_summary_report(trials)
        
        # Display results
        click.echo(f"\n✅ Successfully processed {len(trials)} clinical trials")
        click.echo(f"📁 Files created: {', '.join(created_files)}")
        
        # Display summary
        click.echo(f"\n📊 Summary Report:")
        click.echo(f"   Total trials: {summary['total_trials']}")
        click.echo(f"   Status distribution: {summary['status_distribution']}")
        click.echo(f"   Phase distribution: {summary['phase_distribution']}")
        
        if summary['top_sponsors']:
            click.echo(f"   Top sponsors:")
            for sponsor, count in list(summary['top_sponsors'].items())[:5]:
                click.echo(f"     - {sponsor}: {count} trials")
        
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
    Get detailed information for a specific clinical trial by NCT ID
    
    Example: python main.py get-trial NCT12345678
    """
    api = ClinicalTrialsAPI()
    processor = DataProcessor(output_dir)
    
    logger.info(f"Retrieving trial details for {nct_id}")
    
    try:
        trial = api.get_trial_details(nct_id)
        
        if not trial:
            click.echo(f"❌ Trial {nct_id} not found", err=True)
            return
        
        # Export single trial
        created_files = processor.export_trials(
            trials=[trial],
            format_type=output_format,
            filename_prefix=f"trial_{nct_id}"
        )
        
        click.echo(f"✅ Retrieved trial: {trial.brief_title}")
        click.echo(f"📁 Files created: {', '.join(created_files)}")
        
    except Exception as e:
        logger.error(f"Error retrieving trial {nct_id}: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()

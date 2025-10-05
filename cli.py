#!/usr/bin/env python3
"""
Command-Line Interface for Earnings Call Analyzer
Phase 1 - Core Analysis Features
"""
import click
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.aggregator import EarningsCallAnalyzer
from config.settings import settings


@click.group()
def cli():
    """Earnings Call Analysis Platform - CLI Tool"""
    pass


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output JSON file path', default=None)
@click.option('--no-llm', is_flag=True, help='Disable LLM features for faster analysis')
@click.option('--summary', '-s', is_flag=True, help='Print summary to console')
def analyze(transcript_file, output, no_llm, summary):
    """
    Analyze an earnings call transcript
    
    TRANSCRIPT_FILE: Path to the transcript file (.txt, .md)
    
    Example:
        earnings-analyzer analyze transcript.txt -o results.json -s
    """
    click.echo(f"\n{'='*80}")
    click.echo("EARNINGS CALL ANALYZER - Phase 1")
    click.echo(f"{'='*80}\n")
    
    # Initialize analyzer
    use_llm = not no_llm
    if no_llm:
        click.echo("⚡ Fast mode enabled (LLM features disabled)")
    
    analyzer = EarningsCallAnalyzer(use_llm_features=use_llm)
    
    # Perform analysis
    try:
        results = analyzer.analyze_transcript(transcript_file)
        
        # Save results if output path provided
        if output:
            analyzer.save_results(results, output)
        else:
            # Default output path
            transcript_path = Path(transcript_file)
            output_path = transcript_path.parent / f"{transcript_path.stem}_analysis.json"
            analyzer.save_results(results, str(output_path))
        
        # Print summary if requested
        if summary:
            analyzer.print_summary(results)
        else:
            click.echo("\n✓ Analysis complete! Use --summary flag to see results in console.")
    
    except Exception as e:
        click.echo(f"\n❌ Error during analysis: {str(e)}", err=True)
        if click.confirm("\nShow full traceback?"):
            raise
        sys.exit(1)


@cli.command()
def check_setup():
    """Check if all required components are properly set up"""
    click.echo("\n🔍 Checking Earnings Call Analyzer setup...\n")
    
    issues = []
    
    # Check dictionaries
    click.echo("1. Checking Loughran-McDonald dictionaries...")
    dict_dir = settings.DICTIONARIES_DIR / "loughran_mcdonald"
    required_dicts = ['negative.txt', 'positive.txt', 'uncertainty.txt', 
                     'litigious.txt', 'strong_modal.txt', 'weak_modal.txt', 
                     'constraining.txt']
    
    missing_dicts = []
    for dict_file in required_dicts:
        if not (dict_dir / dict_file).exists():
            missing_dicts.append(dict_file)
    
    if missing_dicts:
        click.echo(f"   ❌ Missing dictionaries: {', '.join(missing_dicts)}")
        click.echo(f"   → Run: python scripts/download_dictionaries.py")
        issues.append("Missing LM dictionaries")
    else:
        click.echo("   ✓ All dictionaries found")
    
    # Check Ollama
    click.echo("\n2. Checking Ollama connection...")
    try:
        from src.models.ollama_client import ollama_client
        if ollama_client.check_model_availability(settings.SENTIMENT_MODEL):
            click.echo(f"   ✓ Ollama connected, model '{settings.SENTIMENT_MODEL}' available")
        else:
            click.echo(f"   ⚠️  Ollama connected, but model '{settings.SENTIMENT_MODEL}' not found")
            click.echo(f"   → Pull model: ollama pull {settings.SENTIMENT_MODEL}")
            issues.append(f"Model {settings.SENTIMENT_MODEL} not available")
    except Exception as e:
        click.echo(f"   ❌ Cannot connect to Ollama: {str(e)}")
        click.echo(f"   → Make sure Ollama is running: ollama serve")
        issues.append("Ollama not running")
    
    # Check data directories
    click.echo("\n3. Checking data directories...")
    required_dirs = [settings.DATA_DIR, settings.DICTIONARIES_DIR, 
                    settings.TRANSCRIPTS_DIR, settings.BENCHMARKS_DIR]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            click.echo(f"   ℹ️  Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
    click.echo("   ✓ All directories ready")
    
    # Summary
    click.echo(f"\n{'='*80}")
    if issues:
        click.echo(f"❌ Setup incomplete - {len(issues)} issue(s) found:")
        for issue in issues:
            click.echo(f"   • {issue}")
        click.echo("\nPlease resolve the issues above before running analysis.")
    else:
        click.echo("✓ All checks passed! System is ready for analysis.")
    click.echo(f"{'='*80}\n")


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
def validate(transcript_file):
    """Validate a transcript file without performing analysis"""
    from src.core.transcript_processor import TranscriptProcessor
    
    click.echo(f"\nValidating transcript: {transcript_file}\n")
    
    processor = TranscriptProcessor()
    
    try:
        transcript = processor.process(transcript_file)
        
        click.echo("✓ Transcript loaded successfully")
        click.echo(f"\nMetadata:")
        click.echo(f"  Company: {transcript.metadata.company_name or 'Not found'}")
        click.echo(f"  Quarter: {transcript.metadata.quarter or 'Not found'} {transcript.metadata.year or ''}")
        click.echo(f"  Date: {transcript.metadata.date or 'Not found'}")
        
        click.echo(f"\nStatistics:")
        click.echo(f"  Words: {transcript.word_count:,}")
        click.echo(f"  Sentences: {transcript.sentence_count:,}")
        click.echo(f"  Speakers identified: {len(transcript.speakers)}")
        click.echo(f"  Sections: {', '.join(transcript.sections.keys())}")
        
        # Validate
        warnings = processor.validate_transcript(transcript)
        
        if warnings:
            click.echo(f"\n⚠️  Validation warnings:")
            for warning in warnings:
                click.echo(f"  • {warning}")
        else:
            click.echo("\n✓ No validation issues found")
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', help='Output directory for results', required=True)
@click.option('--pattern', '-p', default='*.txt', help='File pattern to match (default: *.txt)')
@click.option('--parallel/--sequential', default=True, help='Process in parallel (default: parallel)')
@click.option('--no-llm', is_flag=True, help='Disable LLM features for faster analysis')
def batch(input_dir, output_dir, pattern, parallel, no_llm):
    """
    Batch process multiple transcripts in a directory
    
    INPUT_DIR: Directory containing transcript files
    
    Example:
        earnings-analyzer batch data/transcripts/ -o results/batch1/
    """
    from src.batch_processor import BatchProcessor
    
    click.echo(f"\n{'='*80}")
    click.echo("BATCH PROCESSING MODE")
    click.echo(f"{'='*80}\n")
    
    use_llm = not no_llm
    processor = BatchProcessor(use_llm_features=use_llm, max_workers=3)
    
    try:
        summary = processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            file_pattern=pattern,
            parallel=parallel
        )
        
        click.echo(f"\n✓ Batch processing complete!")
        click.echo(f"  Processed: {summary['processed']}")
        click.echo(f"  Failed: {summary['failed']}")
        
    except Exception as e:
        click.echo(f"\n❌ Error during batch processing: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['pdf', 'md', 'both']), default='both', help='Report format')
@click.option('--output', '-o', help='Output file path (without extension)')
def report(transcript_file, format, output):
    """
    Generate a formatted report (PDF and/or Markdown)
    
    TRANSCRIPT_FILE: Path to the transcript file
    
    Example:
        earnings-analyzer report transcript.txt -f pdf -o my_report
    """
    from src.analysis.aggregator import EarningsCallAnalyzer
    from src.reporting.pdf_generator import PDFReportGenerator
    from src.reporting.markdown_generator import MarkdownReportGenerator
    
    click.echo(f"\n{'='*80}")
    click.echo("GENERATING REPORT")
    click.echo(f"{'='*80}\n")
    
    # Analyze transcript
    click.echo("Analyzing transcript...")
    analyzer = EarningsCallAnalyzer(use_llm_features=True)
    results = analyzer.analyze_transcript(transcript_file)
    
    # Determine output path
    if not output:
        transcript_path = Path(transcript_file)
        output = str(transcript_path.parent / transcript_path.stem)
    
    # Generate reports
    if format in ['pdf', 'both']:
        click.echo("\nGenerating PDF report...")
        pdf_gen = PDFReportGenerator()
        pdf_path = f"{output}_report.pdf"
        pdf_gen.generate_executive_summary(results, pdf_path)
    
    if format in ['md', 'both']:
        click.echo("\nGenerating Markdown report...")
        md_gen = MarkdownReportGenerator()
        md_path = f"{output}_report.md"
        md_gen.generate_executive_summary(results, md_path)
    
    click.echo(f"\n✓ Report generation complete!\n")


@cli.command()
def info():
    """Display system information and configuration"""
    click.echo("\n" + "="*80)
    click.echo("EARNINGS CALL ANALYZER - SYSTEM INFORMATION")
    click.echo("="*80 + "\n")
    
    click.echo("Configuration:")
    click.echo(f"  Project Root: {settings.PROJECT_ROOT}")
    click.echo(f"  Data Directory: {settings.DATA_DIR}")
    click.echo(f"  Ollama Host: {settings.OLLAMA_HOST}")
    click.echo(f"  Sentiment Model: {settings.SENTIMENT_MODEL}")
    click.echo(f"  Contextualization Model: {settings.CONTEXTUALIZATION_MODEL}")
    
    click.echo("\nBenchmarks:")
    click.echo(f"  S&P 500 Net Positivity: {settings.SP500_NET_POSITIVITY}%")
    click.echo(f"  S&P 500 Numeric Transparency: {settings.SP500_NUMERIC_TRANSPARENCY}%")
    
    click.echo("\nAnalysis Settings:")
    click.echo(f"  Hybrid Sentiment Weighting: {settings.HYBRID_SENTIMENT_WEIGHT_LEXICON:.0%} Lexicon / {settings.HYBRID_SENTIMENT_WEIGHT_LLM:.0%} LLM")
    click.echo(f"  LLM Chunk Size: {settings.LLM_CHUNK_SIZE} tokens")
    click.echo(f"  LLM Temperature: {settings.LLM_TEMPERATURE}")
    
    click.echo("\n" + "="*80 + "\n")


if __name__ == '__main__':
    cli()

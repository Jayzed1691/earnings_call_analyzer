#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Command-Line Interface for Earnings Call Analyzer
Phase 2A Enhanced - Includes deception analysis commands
"""
import click
import json
import logging
from pathlib import Path
from config.settings import settings
from config.logging_config import setup_logging

# Initialize logging
setup_logging()


@click.group()
@click.version_option(version="2.0.0-phase2a")
def cli():
	"""Earnings Call Analyzer - Comprehensive financial communication analysis"""
	pass
	
	
@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output JSON file path', default=None)
@click.option('--no-llm', is_flag=True, help='Disable LLM features')
@click.option('--with-deception', is_flag=True, default=True, help='Include Phase 2A deception analysis (default: enabled)')
@click.option('--summary', '-s', is_flag=True, help='Print summary to console')
def analyze(transcript_file, output, no_llm, with_deception, summary):
	"""
	Analyze an earnings call transcript (Phase 1 + Phase 2A)
	
	Example:
		earnings-analyzer analyze transcript.txt --with-deception --summary
	"""
	from src.analysis.aggregator import EarningsCallAnalyzer
	
	# Initialize analyzer
	analyzer = EarningsCallAnalyzer(
		use_llm_features=not no_llm,
		enable_deception_analysis=with_deception
	)
	
	# Analyze
	results = analyzer.analyze_transcript(transcript_file)
	
	# Save results
	if output:
		analyzer.save_results(results, output)
	else:
		# Default output path
		input_path = Path(transcript_file)
		output_path = input_path.with_suffix('.results.json')
		analyzer.save_results(results, str(output_path))
		
	# Print summary
	if summary:
		analyzer.print_summary(results)
		
		
@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
def summary(results_file):
	"""
	Print summary from a results JSON file
	
	Example:
		earnings-analyzer summary results.json
	"""
	from src.analysis.aggregator import EarningsCallAnalyzer, ComprehensiveAnalysisResult
	from dataclasses import fields
	
	# Load results
	with open(results_file, 'r') as f:
		data = json.load(f)
		
	# Reconstruct result object (simplified - in production use proper deserialization)
	# For now, just print key metrics
	click.echo(f"\n{'='*80}")
	click.echo(f"EARNINGS CALL ANALYSIS SUMMARY")
	click.echo(f"Company: {data.get('company_name')} | Quarter: {data.get('quarter')} {data.get('year')}")
	click.echo(f"{'='*80}")
	
	# Phase 1 metrics
	click.echo("\n📊 PHASE 1: CORE METRICS")
	click.echo("-" * 80)
	if 'overall_sentiment' in data:
		sent = data['overall_sentiment']
		click.echo(f"Sentiment: {sent.get('hybrid_label')} ({sent.get('hybrid_sentiment_score'):.2f})")
	if 'overall_complexity' in data:
		comp = data['overall_complexity']
		click.echo(f"Complexity: {comp.get('complexity_level')} ({comp.get('composite_score'):.0f}/100)")
	if 'overall_numerical' in data:
		num = data['overall_numerical']
		click.echo(f"Numerical Transparency: {num.get('numeric_transparency_score'):.2f}%")
		
	# Phase 2A metrics
	if data.get('deception_risk'):
		click.echo("\n⚠️  PHASE 2A: DECEPTION RISK ASSESSMENT")
		click.echo("-" * 80)
		risk = data['deception_risk']
		click.echo(f"Overall Risk: {risk.get('risk_level')} ({risk.get('overall_risk_score'):.0f}/100)")
		click.echo(f"Confidence: {risk.get('confidence'):.0%}")
		
		if risk.get('triggered_flags'):
			click.echo(f"\nTriggered Flags:")
			for flag in risk['triggered_flags'][:5]:
				click.echo(f"  • {flag}")
				
	# Red flags
	if data.get('red_flags'):
		click.echo("\n🚩 RED FLAGS")
		click.echo("-" * 80)
		for flag in data['red_flags']:
			click.echo(f"  • {flag}")
			
	# Strengths
	if data.get('strengths'):
		click.echo("\n✅ STRENGTHS")
		click.echo("-" * 80)
		for strength in data['strengths']:
			click.echo(f"  • {strength}")
			
	click.echo("\n" + "="*80)
	
	
@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path', default=None)
def deception(transcript_file, output):
	"""
	Run ONLY deception analysis on a transcript (Phase 2A)
	
	Example:
		earnings-analyzer deception transcript.txt -o deception_report.json
	"""
	from src.analysis.aggregator import EarningsCallAnalyzer
	
	click.echo("\n🔍 Running deception-focused analysis...")
	
	# Initialize with deception only
	analyzer = EarningsCallAnalyzer(
		use_llm_features=True,
		enable_deception_analysis=True
	)
	
	# Analyze
	results = analyzer.analyze_transcript(transcript_file)
	
	# Extract deception-specific results
	deception_report = {
		'company': results.company_name,
		'quarter': results.quarter,
		'year': results.year,
		'timestamp': results.timestamp,
		'deception_risk': results.deception_risk.__dict__ if results.deception_risk else None,
		'evasiveness': results.evasiveness_scores.__dict__ if results.evasiveness_scores else None,
		'qa_analysis': [qa.__dict__ for qa in results.qa_analysis] if results.qa_analysis else []
	}
	
	# Save
	if output:
		output_path = Path(output)
	else:
		input_path = Path(transcript_file)
		output_path = input_path.with_suffix('.deception.json')
		
	with open(output_path, 'w') as f:
		json.dump(deception_report, f, indent=2, default=str)
		
	click.echo(f"\n✓ Deception analysis saved to: {output_path}")
	
	# Print quick summary
	if results.deception_risk:
		click.echo(f"\nRisk Level: {results.deception_risk.risk_level}")
		click.echo(f"Risk Score: {results.deception_risk.overall_risk_score:.0f}/100")
		click.echo(f"Flags: {len(results.deception_risk.triggered_flags)}")
		
		
@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--metric', '-m', help='Specific metric to display', default=None)
def inspect(results_file, metric):
	"""
	Inspect detailed metrics from analysis results
	
	Example:
		earnings-analyzer inspect results.json --metric deception_risk
	"""
	with open(results_file, 'r') as f:
		data = json.load(f)
		
	if metric:
		if metric in data:
			click.echo(f"\n{metric.upper()}:")
			click.echo(json.dumps(data[metric], indent=2))
		else:
			click.echo(f"Metric '{metric}' not found in results")
			click.echo(f"\nAvailable metrics:")
			for key in data.keys():
				click.echo(f"  - {key}")
	else:
		click.echo("\nAll metrics:")
		for key in data.keys():
			click.echo(f"  - {key}")
			
			
@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
@click.option('--with-deception', is_flag=True, default=True)
def batch(directory, format, with_deception):
	"""
	Batch process all transcripts in a directory
	
	Example:
		earnings-analyzer batch ./transcripts/ --with-deception
	"""
	from src.analysis.aggregator import EarningsCallAnalyzer
	import glob
	
	dir_path = Path(directory)
	transcript_files = list(dir_path.glob('*.txt')) + list(dir_path.glob('*.md'))
	
	if not transcript_files:
		click.echo(f"No transcript files found in {directory}")
		return
	
	click.echo(f"\n📦 Batch processing {len(transcript_files)} transcripts...")
	
	analyzer = EarningsCallAnalyzer(
		use_llm_features=True,
		enable_deception_analysis=with_deception
	)
	
	results_list = []
	
	for i, file_path in enumerate(transcript_files, 1):
		click.echo(f"\n[{i}/{len(transcript_files)}] Processing: {file_path.name}")
		
		try:
			results = analyzer.analyze_transcript(str(file_path))
			
			# Save individual result
			output_path = file_path.with_suffix('.results.json')
			analyzer.save_results(results, str(output_path))
			
			# Add to batch results
			results_list.append({
				'file': file_path.name,
				'company': results.company_name,
				'quarter': results.quarter,
				'year': results.year,
				'sentiment_score': results.overall_sentiment.hybrid_sentiment_score,
				'complexity_score': results.overall_complexity.composite_score,
				'transparency_score': results.overall_numerical.numeric_transparency_score,
				'deception_risk_score': results.deception_risk.overall_risk_score if results.deception_risk else None,
				'evasiveness_score': results.evasiveness_scores.overall_evasiveness if results.evasiveness_scores else None,
			})
			
		except Exception as e:
			click.echo(f"  ❌ Error: {str(e)}")
			continue
		
	# Save batch summary
	batch_output = dir_path / f"batch_results.{format}"
	
	if format == 'json':
		with open(batch_output, 'w') as f:
			json.dump(results_list, f, indent=2)
	elif format == 'csv':
		import csv
		with open(batch_output, 'w', newline='') as f:
			if results_list:
				writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
				writer.writeheader()
				writer.writerows(results_list)
				
	click.echo(f"\n✓ Batch processing complete!")
	click.echo(f"Summary saved to: {batch_output}")
	
	
@cli.command()
def config():
	"""Show current configuration"""
	click.echo("\n📋 CONFIGURATION")
	click.echo("="*60)
	click.echo(f"Project Root: {settings.PROJECT_ROOT}")
	click.echo(f"Data Directory: {settings.DATA_DIR}")
	click.echo(f"\nOllama:")
	click.echo(f"  Host: {settings.OLLAMA_HOST}")
	click.echo(f"  Sentiment Model: {settings.SENTIMENT_MODEL}")
	click.echo(f"\nFeature Flags:")
	click.echo(f"  Phase 2A Deception Analysis: {settings.ENABLE_DECEPTION_ANALYSIS}")
	click.echo(f"  Evasiveness Analysis: {settings.ENABLE_EVASIVENESS_ANALYSIS}")
	click.echo(f"  Q&A Analysis: {settings.ENABLE_QA_ANALYSIS}")
	click.echo(f"\nBenchmarks:")
	click.echo(f"  S&P 500 Net Positivity: {settings.SP500_NET_POSITIVITY}")
	click.echo(f"  S&P 500 Numeric Transparency: {settings.SP500_NUMERIC_TRANSPARENCY}%")
	click.echo(f"  S&P 500 Evasiveness Baseline: {settings.SP500_EVASIVENESS_BASELINE}")
	click.echo(f"\nThresholds:")
	click.echo(f"  Deception Risk Warning: {settings.DECEPTION_RISK_WARNING}")
	click.echo(f"  Deception Risk Critical: {settings.DECEPTION_RISK_CRITICAL}")
	click.echo(f"  Question Avoidance Alert: {settings.QUESTION_AVOIDANCE_ALERT}%")
	click.echo("="*60)
	
	
if __name__ == '__main__':
	cli()
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
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('--output', '-o', help='Output file path for formatted transcript', default=None)
@click.option('--validate-only', is_flag=True, help='Only validate, do not save')
def prepare(input_file, output, validate_only):
	"""
	Interactive transcript preparation wizard for non-technical users

	Guides you through:
	- Metadata entry (company, ticker, quarter, year, date)
	- Speaker identification and correction
	- Section validation
	- Format verification

	Example:
		earnings-analyzer prepare raw_transcript.txt -o formatted.txt
		earnings-analyzer prepare  # Interactive mode from scratch
	"""
	from src.core.transcript_processor import TranscriptProcessor, TranscriptMetadata
	import re
	from datetime import datetime

	click.echo("\n" + "="*70)
	click.echo("📝 TRANSCRIPT PREPARATION WIZARD")
	click.echo("="*70)
	click.echo("\nThis wizard will help you prepare an earnings call transcript")
	click.echo("for analysis. Follow the prompts to provide required information.\n")

	# Step 1: Load or create transcript text
	if input_file:
		click.echo(f"📂 Loading transcript from: {input_file}")
		with open(input_file, 'r', encoding='utf-8') as f:
			transcript_text = f.read()
		click.echo(f"   ✓ Loaded {len(transcript_text)} characters\n")
	else:
		click.echo("📝 No input file provided. You can paste transcript text.\n")
		click.echo("Paste your transcript (press Ctrl+D when done on Unix/Mac, Ctrl+Z then Enter on Windows):")
		import sys
		transcript_text = sys.stdin.read()
		if not transcript_text.strip():
			click.echo("❌ No text provided. Exiting.")
			return

	# Step 2: Collect metadata interactively
	click.echo("\n" + "-"*70)
	click.echo("STEP 1: METADATA ENTRY")
	click.echo("-"*70)

	company_name = click.prompt("Company Name (e.g., 'TechCorp Industries')", type=str)

	# Ticker validation
	while True:
		ticker = click.prompt("Stock Ticker (e.g., 'TECH')", type=str).upper()
		if re.match(r'^[A-Z]{1,5}$', ticker):
			break
		click.echo("   ⚠ Ticker should be 1-5 uppercase letters. Try again.")

	# Quarter selection
	quarter = click.prompt("Quarter", type=click.Choice(['Q1', 'Q2', 'Q3', 'Q4'], case_sensitive=False)).upper()

	# Year validation
	current_year = datetime.now().year
	while True:
		year = click.prompt("Year", type=int, default=current_year)
		if 2000 <= year <= current_year + 1:
			break
		click.echo(f"   ⚠ Year should be between 2000 and {current_year + 1}. Try again.")

	# Date entry (optional but recommended)
	date_str = click.prompt("Call Date (MM/DD/YYYY)", default="", show_default=False)
	if date_str:
		try:
			datetime.strptime(date_str, "%m/%d/%Y")
		except ValueError:
			click.echo("   ⚠ Invalid date format, leaving blank")
			date_str = ""

	click.echo("\n✓ Metadata collected:")
	click.echo(f"   Company: {company_name}")
	click.echo(f"   Ticker: {ticker}")
	click.echo(f"   Quarter: {quarter}")
	click.echo(f"   Year: {year}")
	if date_str:
		click.echo(f"   Date: {date_str}")

	# Step 3: Parse and validate transcript structure
	click.echo("\n" + "-"*70)
	click.echo("STEP 2: TRANSCRIPT VALIDATION")
	click.echo("-"*70)

	processor = TranscriptProcessor()

	# Check if transcript already has metadata header
	has_header = transcript_text.strip().startswith("Company:")

	if has_header:
		click.echo("✓ Transcript appears to have metadata header")
		# Try to parse it
		try:
			temp_path = Path(input_file) if input_file else Path("temp_transcript.txt")
			if not input_file:
				with open(temp_path, 'w', encoding='utf-8') as f:
					f.write(transcript_text)

			parsed = processor.process_file(str(temp_path))

			click.echo(f"✓ Successfully parsed transcript")
			click.echo(f"   - Word count: {parsed.word_count}")
			click.echo(f"   - Sentence count: {parsed.sentence_count}")
			click.echo(f"   - Speakers detected: {len(parsed.speakers)}")
			click.echo(f"   - Sections detected: {len(parsed.sections)}")

			if parsed.speakers:
				click.echo(f"\n   Detected speakers:")
				for speaker in list(parsed.speakers.keys())[:5]:
					click.echo(f"      • {speaker}")
				if len(parsed.speakers) > 5:
					click.echo(f"      ... and {len(parsed.speakers) - 5} more")

			if parsed.sections:
				click.echo(f"\n   Detected sections:")
				for section in parsed.sections.keys():
					click.echo(f"      • {section}")

			# Ask if user wants to update metadata
			if click.confirm("\n   Do you want to update the metadata in the transcript?", default=False):
				has_header = False  # Will rebuild with new metadata
			else:
				# Use existing structure
				if validate_only:
					click.echo("\n✓ Validation complete. Transcript is properly formatted.")
					return

				if output:
					# Just copy to output
					with open(output, 'w', encoding='utf-8') as f:
						f.write(transcript_text)
					click.echo(f"\n✓ Transcript saved to: {output}")
				else:
					click.echo("\n✓ Transcript is ready for analysis.")
					click.echo(f"   Run: python cli.py analyze {input_file}")
				return

		except Exception as e:
			click.echo(f"⚠ Parsing failed: {str(e)}")
			click.echo("   Will help you format the transcript...")
			has_header = False

	# Step 4: Build formatted transcript
	if not has_header:
		click.echo("\n" + "-"*70)
		click.echo("STEP 3: FORMATTING TRANSCRIPT")
		click.echo("-"*70)

		# Build metadata header
		formatted_lines = [
			f"Company: {company_name}",
			f"Ticker: {ticker}",
			f"Quarter: {quarter}",
			f"Year: {year}",
		]

		if date_str:
			formatted_lines.append(f"Date: {date_str}")

		formatted_lines.append("")  # Blank line

		# Check if transcript has section markers
		has_sections = any(marker in transcript_text.upper() for marker in [
			"PREPARED REMARKS", "Q&A", "QUESTIONS AND ANSWERS", "OPERATOR:"
		])

		if has_sections:
			click.echo("✓ Detected section markers in transcript")
			# Just append the content
			formatted_lines.append(transcript_text.strip())
		else:
			click.echo("⚠ No section markers detected")
			click.echo("\nTranscript should have sections like:")
			click.echo("   PREPARED REMARKS")
			click.echo("   QUESTIONS AND ANSWERS")
			click.echo("\nYou can add these manually or the system will treat it as one section.")

			if click.confirm("   Add 'PREPARED REMARKS' header?", default=True):
				formatted_lines.append("PREPARED REMARKS")
				formatted_lines.append("")

			formatted_lines.append(transcript_text.strip())

		final_transcript = "\n".join(formatted_lines)

		# Preview
		click.echo("\n" + "-"*70)
		click.echo("PREVIEW (first 500 characters):")
		click.echo("-"*70)
		click.echo(final_transcript[:500])
		if len(final_transcript) > 500:
			click.echo("...")
		click.echo("-"*70)

		# Validate the formatted transcript
		click.echo("\n⏳ Validating formatted transcript...")

		try:
			# Save to temp file for validation
			temp_path = Path("temp_validation.txt")
			with open(temp_path, 'w', encoding='utf-8') as f:
				f.write(final_transcript)

			parsed = processor.process_file(str(temp_path))

			click.echo("✓ Validation successful!")
			click.echo(f"   - Word count: {parsed.word_count}")
			click.echo(f"   - Sentence count: {parsed.sentence_count}")
			click.echo(f"   - Speakers detected: {len(parsed.speakers)}")

			# Check for potential issues
			warnings = []
			if parsed.word_count < settings.MIN_TRANSCRIPT_LENGTH:
				warnings.append(f"Word count ({parsed.word_count}) is below recommended minimum ({settings.MIN_TRANSCRIPT_LENGTH})")
			if len(parsed.speakers) == 0:
				warnings.append("No speakers detected - make sure to use format 'Name - Title: text'")
			if len(parsed.sections) < 2:
				warnings.append("Only one section detected - consider adding section markers")

			if warnings:
				click.echo("\n⚠ Warnings:")
				for warning in warnings:
					click.echo(f"   • {warning}")

			# Clean up temp file
			temp_path.unlink()

		except Exception as e:
			click.echo(f"❌ Validation failed: {str(e)}")
			click.echo("\nPlease check the format and try again.")
			if temp_path.exists():
				temp_path.unlink()
			return

		# Step 5: Save or display
		if validate_only:
			click.echo("\n✓ Validation complete. Transcript is properly formatted.")
			return

		# Determine output path
		if output:
			output_path = Path(output)
		elif input_file:
			input_path = Path(input_file)
			output_path = input_path.with_stem(input_path.stem + "_formatted")
		else:
			output_path = Path(f"{ticker}_{quarter}{year}_transcript.txt")

		# Save
		with open(output_path, 'w', encoding='utf-8') as f:
			f.write(final_transcript)

		click.echo("\n" + "="*70)
		click.echo("✓ TRANSCRIPT PREPARATION COMPLETE!")
		click.echo("="*70)
		click.echo(f"Formatted transcript saved to: {output_path}")
		click.echo("\nNext steps:")
		click.echo(f"   1. Review the transcript: cat {output_path}")
		click.echo(f"   2. Run analysis: python cli.py analyze {output_path} --summary")
		click.echo("="*70)


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
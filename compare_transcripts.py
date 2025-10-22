#!/usr/bin/env python3
"""
Transcript Comparison Tool
Compare earnings call metrics across quarters or between companies
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.aggregator import EarningsCallAnalyzer
from src.utils.transcript_parser import TranscriptParser


@dataclass
class MetricComparison:
    """Container for metric comparison results"""
    metric_name: str
    value1: float
    value2: float
    change: float
    pct_change: Optional[float]
    direction: str  # 'up', 'down', 'unchanged'

    def format_change(self) -> str:
        """Format change with arrows and colors"""
        if self.direction == 'up':
            arrow = '↑'
            sign = '+'
        elif self.direction == 'down':
            arrow = '↓'
            sign = ''
        else:
            arrow = '→'
            sign = ''

        if self.pct_change is not None:
            return f"{arrow} {sign}{self.change:.2f} ({sign}{self.pct_change:.1f}%)"
        else:
            return f"{arrow} {sign}{self.change:.2f}"


def calculate_change(val1: float, val2: float, is_percentage: bool = False) -> MetricComparison:
    """Calculate change between two values"""
    change = val2 - val1

    # Calculate percentage change
    if val1 != 0:
        pct_change = (change / abs(val1)) * 100
    else:
        pct_change = None

    # Determine direction
    if abs(change) < 0.01:  # Threshold for "unchanged"
        direction = 'unchanged'
    elif change > 0:
        direction = 'up'
    else:
        direction = 'down'

    return MetricComparison(
        metric_name="",
        value1=val1,
        value2=val2,
        change=change,
        pct_change=pct_change,
        direction=direction
    )


def compare_calls(file1: Path, file2: Path, label1: str = "Q1", label2: str = "Q2") -> Dict[str, Any]:
    """
    Compare two earnings call transcripts

    Args:
        file1: Path to first transcript
        file2: Path to second transcript
        label1: Label for first transcript (e.g., "Q1 2024")
        label2: Label for second transcript (e.g., "Q2 2024")

    Returns:
        Dictionary containing comparison results
    """
    print(f"\n{'='*80}")
    print(f"📊 EARNINGS CALL COMPARISON: {label1} vs {label2}")
    print(f"{'='*80}\n")

    # Initialize analyzer
    analyzer = EarningsCallAnalyzer()

    # Analyze both transcripts
    print(f"Analyzing {label1}...")
    results1 = analyzer.analyze_transcript(str(file1))

    print(f"Analyzing {label2}...")
    results2 = analyzer.analyze_transcript(str(file2))

    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}\n")

    comparisons = {}

    # 1. Sentence-Level Density Metrics
    if results1.sentence_density_metrics and results2.sentence_density_metrics:
        print("📈 SENTENCE-LEVEL DENSITY METRICS")
        print("-" * 80)

        sdm1 = results1.sentence_density_metrics
        sdm2 = results2.sentence_density_metrics

        # Total sentences
        total_change = calculate_change(sdm1.total_sentences, sdm2.total_sentences)
        print(f"Total Sentences:        {sdm1.total_sentences:>6} → {sdm2.total_sentences:>6}  {total_change.format_change()}")

        # Dense sentences
        dense_change = calculate_change(
            sdm1.proportion_numeric_dense * 100,
            sdm2.proportion_numeric_dense * 100
        )
        print(f"Dense Sentences (>10%): {sdm1.proportion_numeric_dense:>6.1%} → {sdm2.proportion_numeric_dense:>6.1%}  {dense_change.format_change()}")

        # Narrative sentences
        narrative_change = calculate_change(
            sdm1.proportion_narrative * 100,
            sdm2.proportion_narrative * 100
        )
        print(f"Narrative (0%):         {sdm1.proportion_narrative:>6.1%} → {sdm2.proportion_narrative:>6.1%}  {narrative_change.format_change()}")

        # Mean density
        mean_change = calculate_change(sdm1.mean_numeric_density, sdm2.mean_numeric_density)
        print(f"Mean Density:           {sdm1.mean_numeric_density:>6.2f}% → {sdm2.mean_numeric_density:>6.2f}%  {mean_change.format_change()}")

        comparisons['density'] = {
            'total_sentences': total_change.__dict__,
            'dense_proportion': dense_change.__dict__,
            'narrative_proportion': narrative_change.__dict__,
            'mean_density': mean_change.__dict__
        }

    # 2. Distribution Patterns
    if results1.distribution_patterns and results2.distribution_patterns:
        print(f"\n📊 DISTRIBUTION PATTERNS")
        print("-" * 80)

        dp1 = results1.distribution_patterns
        dp2 = results2.distribution_patterns

        print(f"Pattern Type:           {dp1.pattern_type:>15} → {dp2.pattern_type:>15}")
        print(f"Pattern Confidence:     {dp1.pattern_confidence:>14.1%} → {dp2.pattern_confidence:>14.1%}")

        # Positional density
        beg_change = calculate_change(dp1.beginning_density, dp2.beginning_density)
        print(f"Beginning Density:      {dp1.beginning_density:>14.2f}% → {dp2.beginning_density:>14.2f}%  {beg_change.format_change()}")

        mid_change = calculate_change(dp1.middle_density, dp2.middle_density)
        print(f"Middle Density:         {dp1.middle_density:>14.2f}% → {dp2.middle_density:>14.2f}%  {mid_change.format_change()}")

        end_change = calculate_change(dp1.end_density, dp2.end_density)
        print(f"End Density:            {dp1.end_density:>14.2f}% → {dp2.end_density:>14.2f}%  {end_change.format_change()}")

        # Q&A differential
        qa_change = calculate_change(dp1.qa_density_differential, dp2.qa_density_differential)
        print(f"Q&A Differential:       {dp1.qa_density_differential:>14.2f}% → {dp2.qa_density_differential:>14.2f}%  {qa_change.format_change()}")

        comparisons['patterns'] = {
            'pattern_type_change': f"{dp1.pattern_type} → {dp2.pattern_type}",
            'beginning_density': beg_change.__dict__,
            'middle_density': mid_change.__dict__,
            'end_density': end_change.__dict__,
            'qa_differential': qa_change.__dict__
        }

    # 3. Informativeness Metrics
    if results1.informativeness_metrics and results2.informativeness_metrics:
        print(f"\n💡 INFORMATIVENESS METRICS")
        print("-" * 80)

        im1 = results1.informativeness_metrics
        im2 = results2.informativeness_metrics

        # NIR (Numeric Inclusion Ratio) - KEY METRIC
        nir_change = calculate_change(im1.numeric_inclusion_ratio * 100, im2.numeric_inclusion_ratio * 100)
        print(f"NIR (Numeric Inclusion):{im1.numeric_inclusion_ratio:>6.2%} → {im2.numeric_inclusion_ratio:>6.2%}  {nir_change.format_change()}")

        # Informativeness Score
        info_change = calculate_change(im1.informativeness_score, im2.informativeness_score)
        print(f"Informativeness Score:  {im1.informativeness_score:>6.1f} → {im2.informativeness_score:>6.1f}  {info_change.format_change()}")

        # Forecast Relevance
        forecast_change = calculate_change(im1.forecast_relevance_score, im2.forecast_relevance_score)
        print(f"Forecast Relevance:     {im1.forecast_relevance_score:>6.1f} → {im2.forecast_relevance_score:>6.1f}  {forecast_change.format_change()}")

        # Transparency tier
        print(f"Transparency Tier:      {im1.transparency_tier:>15} → {im2.transparency_tier:>15}")

        # Disclosure level
        print(f"Disclosure Level:       {im1.quantitative_disclosure_level:>15} → {im2.quantitative_disclosure_level:>15}")

        comparisons['informativeness'] = {
            'nir': nir_change.__dict__,
            'informativeness_score': info_change.__dict__,
            'forecast_relevance': forecast_change.__dict__,
            'transparency_tier_change': f"{im1.transparency_tier} → {im2.transparency_tier}",
            'disclosure_level_change': f"{im1.quantitative_disclosure_level} → {im2.quantitative_disclosure_level}"
        }

    # 4. Overall Sentiment (if available)
    if results1.overall_sentiment and results2.overall_sentiment:
        print(f"\n😊 SENTIMENT METRICS")
        print("-" * 80)

        sent1 = results1.overall_sentiment
        sent2 = results2.overall_sentiment

        net_pos_change = calculate_change(sent1.net_positivity, sent2.net_positivity)
        print(f"Net Positivity:         {sent1.net_positivity:>6.2f} → {sent2.net_positivity:>6.2f}  {net_pos_change.format_change()}")

        pos_change = calculate_change(sent1.positive_ratio * 100, sent2.positive_ratio * 100)
        print(f"Positive Ratio:         {sent1.positive_ratio:>6.1%} → {sent2.positive_ratio:>6.1%}  {pos_change.format_change()}")

        comparisons['sentiment'] = {
            'net_positivity': net_pos_change.__dict__,
            'positive_ratio': pos_change.__dict__
        }

    # 5. Numerical Analysis (legacy metrics)
    if results1.overall_numerical and results2.overall_numerical:
        print(f"\n🔢 NUMERICAL ANALYSIS")
        print("-" * 80)

        num1 = results1.overall_numerical
        num2 = results2.overall_numerical

        trans_change = calculate_change(num1.numeric_transparency_score, num2.numeric_transparency_score)
        print(f"Transparency Score:     {num1.numeric_transparency_score:>6.2f}% → {num2.numeric_transparency_score:>6.2f}%  {trans_change.format_change()}")

        spec_change = calculate_change(num1.numerical_specificity_index, num2.numerical_specificity_index)
        print(f"Specificity Index:      {num1.numerical_specificity_index:>6.2f} → {num2.numerical_specificity_index:>6.2f}  {spec_change.format_change()}")

        comparisons['numerical'] = {
            'transparency_score': trans_change.__dict__,
            'specificity_index': spec_change.__dict__
        }

    # Summary insights
    print(f"\n{'='*80}")
    print("📋 SUMMARY INSIGHTS")
    print(f"{'='*80}\n")

    if results1.informativeness_metrics and results2.informativeness_metrics:
        im1 = results1.informativeness_metrics
        im2 = results2.informativeness_metrics

        # Overall trend
        info_diff = im2.informativeness_score - im1.informativeness_score
        if info_diff > 5:
            trend = "📈 SIGNIFICANT IMPROVEMENT"
        elif info_diff > 0:
            trend = "↗️  Slight improvement"
        elif info_diff < -5:
            trend = "📉 SIGNIFICANT DECLINE"
        elif info_diff < 0:
            trend = "↘️  Slight decline"
        else:
            trend = "→ No significant change"

        print(f"Overall Informativeness: {trend}")

        # NIR trend
        nir_diff = (im2.numeric_inclusion_ratio - im1.numeric_inclusion_ratio) * 100
        if nir_diff > 5:
            print(f"Numeric Inclusion:       More quantitative (+{nir_diff:.1f}pp)")
        elif nir_diff < -5:
            print(f"Numeric Inclusion:       Less quantitative ({nir_diff:.1f}pp)")
        else:
            print(f"Numeric Inclusion:       Stable ({nir_diff:+.1f}pp)")

        # Pattern shift
        if results1.distribution_patterns and results2.distribution_patterns:
            dp1 = results1.distribution_patterns
            dp2 = results2.distribution_patterns
            if dp1.pattern_type != dp2.pattern_type:
                print(f"Pattern Shift:           {dp1.pattern_type.upper()} → {dp2.pattern_type.upper()}")

    print(f"\n{'='*80}\n")

    return {
        'label1': label1,
        'label2': label2,
        'file1': str(file1),
        'file2': str(file2),
        'comparisons': comparisons
    }


@click.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--label1', default='Call 1', help='Label for first transcript (e.g., "Q1 2024")')
@click.option('--label2', default='Call 2', help='Label for second transcript (e.g., "Q2 2024")')
@click.option('--output', '-o', type=click.Path(), help='Save comparison to JSON file')
def main(file1: str, file2: str, label1: str, label2: str, output: Optional[str]):
    """
    Compare two earnings call transcripts

    Example:
        python compare_transcripts.py q1_2024.txt q2_2024.txt --label1 "Q1 2024" --label2 "Q2 2024"
    """
    results = compare_calls(Path(file1), Path(file2), label1, label2)

    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Comparison saved to: {output}")


if __name__ == '__main__':
    main()

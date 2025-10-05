"""
Main Analysis Aggregator
Combines all analysis modules and orchestrates the complete pipeline
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime

from src.core.transcript_processor import TranscriptProcessor, ProcessedTranscript
from src.analysis.sentiment.hybrid_scorer import HybridSentimentAnalyzer, HybridSentimentScores
from src.analysis.complexity.readability import ComplexityAnalyzer, ComplexityScores
from src.analysis.numerical.transparency import NumericalAnalyzer, NumericalScores


@dataclass
class ComprehensiveAnalysisResult:
    """Complete analysis results for a transcript"""
    # Metadata
    timestamp: str
    company_name: str
    quarter: str
    year: int
    
    # Overall metrics
    overall_sentiment: HybridSentimentScores
    overall_complexity: ComplexityScores
    overall_numerical: NumericalScores
    
    # Section-specific metrics
    prepared_remarks_sentiment: HybridSentimentScores
    qa_sentiment: HybridSentimentScores
    prepared_remarks_complexity: ComplexityScores
    qa_complexity: ComplexityScores
    
    # Speaker-specific metrics (top 2: CEO, CFO)
    ceo_metrics: Dict[str, Any]
    cfo_metrics: Dict[str, Any]
    
    # Key insights
    key_findings: list
    red_flags: list
    strengths: list
    
    # Raw transcript info
    word_count: int
    sentence_count: int


class EarningsCallAnalyzer:
    """Main analyzer that orchestrates all analysis modules"""
    
    def __init__(self, use_llm_features: bool = True):
        """
        Initialize main analyzer
        
        Args:
            use_llm_features: Whether to use LLM-based features (slower but more accurate)
        """
        self.transcript_processor = TranscriptProcessor()
        self.sentiment_analyzer = HybridSentimentAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.numerical_analyzer = NumericalAnalyzer(use_llm_contextualization=use_llm_features)
        self.use_llm = use_llm_features
    
    def analyze_transcript(self, file_path: str) -> ComprehensiveAnalysisResult:
        """
        Perform complete analysis on a transcript
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            ComprehensiveAnalysisResult object
        """
        print(f"Processing transcript: {file_path}")
        
        # Step 1: Process transcript
        print("  → Preprocessing text...")
        transcript = self.transcript_processor.process(file_path)
        
        # Validate
        warnings = self.transcript_processor.validate_transcript(transcript)
        if warnings:
            print(f"  ⚠️  Warnings:")
            for warning in warnings:
                print(f"     - {warning}")
        
        # Step 2: Overall analysis
        print("  → Analyzing overall sentiment...")
        overall_sentiment = self.sentiment_analyzer.analyze(transcript.cleaned_text)
        
        print("  → Analyzing language complexity...")
        overall_complexity = self.complexity_analyzer.analyze(transcript.cleaned_text)
        
        print("  → Analyzing numerical content...")
        overall_numerical = self.numerical_analyzer.analyze(transcript.cleaned_text)
        
        # Step 3: Section analysis
        print("  → Analyzing sections (Prepared Remarks vs Q&A)...")
        section_sentiment = self.sentiment_analyzer.analyze_by_section(transcript.sections)
        section_complexity = self.complexity_analyzer.analyze_by_section(transcript.sections)
        
        # Step 4: Speaker analysis
        print("  → Analyzing speakers...")
        speaker_sentiment = self.sentiment_analyzer.analyze_by_speaker(transcript.speakers)
        speaker_complexity = self.complexity_analyzer.analyze_by_speaker(transcript.speakers)
        speaker_numerical = self.numerical_analyzer.analyze_by_speaker(transcript.speakers)
        
        # Step 5: Generate insights
        print("  → Generating insights and identifying patterns...")
        key_findings, red_flags, strengths = self._generate_insights(
            overall_sentiment,
            overall_complexity,
            overall_numerical,
            section_sentiment,
            section_complexity
        )
        
        # Compile results
        result = ComprehensiveAnalysisResult(
            timestamp=datetime.now().isoformat(),
            company_name=transcript.metadata.company_name or "Unknown",
            quarter=transcript.metadata.quarter or "Unknown",
            year=transcript.metadata.year or 0,
            overall_sentiment=overall_sentiment,
            overall_complexity=overall_complexity,
            overall_numerical=overall_numerical,
            prepared_remarks_sentiment=section_sentiment.get('prepared_remarks'),
            qa_sentiment=section_sentiment.get('qa'),
            prepared_remarks_complexity=section_complexity.get('prepared_remarks'),
            qa_complexity=section_complexity.get('qa'),
            ceo_metrics=self._compile_speaker_metrics('ceo', speaker_sentiment, 
                                                      speaker_complexity, speaker_numerical),
            cfo_metrics=self._compile_speaker_metrics('cfo', speaker_sentiment,
                                                      speaker_complexity, speaker_numerical),
            key_findings=key_findings,
            red_flags=red_flags,
            strengths=strengths,
            word_count=transcript.word_count,
            sentence_count=transcript.sentence_count
        )
        
        print("✓ Analysis complete!")
        return result
    
    def _compile_speaker_metrics(
        self,
        speaker_key: str,
        sentiment: Dict,
        complexity: Dict,
        numerical: Dict
    ) -> Dict[str, Any]:
        """Compile metrics for a specific speaker"""
        metrics = {}
        
        if speaker_key in sentiment:
            metrics['sentiment'] = asdict(sentiment[speaker_key])
        
        if speaker_key in complexity:
            metrics['complexity'] = asdict(complexity[speaker_key])
        
        if speaker_key in numerical:
            metrics['numerical'] = asdict(numerical[speaker_key])
        
        return metrics
    
    def _generate_insights(
        self,
        overall_sentiment: HybridSentimentScores,
        overall_complexity: ComplexityScores,
        overall_numerical: NumericalScores,
        section_sentiment: Dict,
        section_complexity: Dict
    ) -> tuple:
        """
        Generate key findings, red flags, and strengths
        
        Returns:
            Tuple of (key_findings, red_flags, strengths)
        """
        key_findings = []
        red_flags = []
        strengths = []
        
        # Sentiment insights
        if overall_sentiment.hybrid_sentiment_score > 0.3:
            key_findings.append(f"Strong positive sentiment (score: {overall_sentiment.hybrid_sentiment_score:.2f})")
            strengths.append("Optimistic tone throughout the call")
        elif overall_sentiment.hybrid_sentiment_score < -0.3:
            key_findings.append(f"Negative sentiment (score: {overall_sentiment.hybrid_sentiment_score:.2f})")
            red_flags.append("Pessimistic or defensive language detected")
        
        # Complexity insights
        if overall_complexity.composite_score > 70:
            key_findings.append(f"High language complexity ({overall_complexity.complexity_level})")
            red_flags.append(f"Language complexity score of {overall_complexity.composite_score:.0f} may indicate obfuscation")
        elif overall_complexity.composite_score < 40:
            strengths.append("Clear, accessible language")
        
        # Numerical transparency insights
        if overall_numerical.vs_sp500_benchmark == "above":
            strengths.append(f"Above-average numerical transparency ({overall_numerical.numeric_transparency_score:.2f}% vs {settings.SP500_NUMERIC_TRANSPARENCY}% benchmark)")
        elif overall_numerical.vs_sp500_benchmark == "below":
            red_flags.append(f"Below-average numerical transparency ({overall_numerical.numeric_transparency_score:.2f}% vs {settings.SP500_NUMERIC_TRANSPARENCY}% benchmark)")
        
        # Contextualization quality
        if overall_numerical.contextualization_quality_score < 0.5:
            red_flags.append(f"Poor numerical contextualization (score: {overall_numerical.contextualization_quality_score:.2f})")
        elif overall_numerical.contextualization_quality_score > 0.7:
            strengths.append("Well-contextualized quantitative data")
        
        # Forward vs backward numerical density
        if overall_numerical.forward_to_backward_ratio < 0.7:
            key_findings.append("Limited forward-looking quantitative guidance")
            red_flags.append(f"Forward-looking numerical density ({overall_numerical.forward_looking_density:.2f}%) significantly lower than backward-looking")
        
        # Section comparisons
        if 'prepared_remarks' in section_sentiment and 'qa' in section_sentiment:
            prep_score = section_sentiment['prepared_remarks'].hybrid_sentiment_score
            qa_score = section_sentiment['qa'].hybrid_sentiment_score
            
            if prep_score - qa_score > 0.3:
                key_findings.append("Sentiment drops significantly in Q&A section")
                red_flags.append("Defensive or evasive responses during analyst questions")
        
        if 'prepared_remarks' in section_complexity and 'qa' in section_complexity:
            prep_complex = section_complexity['prepared_remarks'].composite_score
            qa_complex = section_complexity['qa'].composite_score
            
            if qa_complex > prep_complex + 15:
                red_flags.append("Q&A responses are notably more complex than prepared remarks")
        
        # Ensure we have at least some findings
        if not key_findings:
            key_findings.append("Standard earnings call communication patterns observed")
        
        return key_findings, red_flags, strengths
    
    def save_results(self, results: ComprehensiveAnalysisResult, output_path: str) -> None:
        """
        Save analysis results to JSON file
        
        Args:
            results: Analysis results
            output_path: Path to save JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict (handling nested dataclasses)
        results_dict = asdict(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"Results saved to: {output_path}")
    
    def print_summary(self, results: ComprehensiveAnalysisResult) -> None:
        """Print a human-readable summary of results"""
        print("\n" + "="*80)
        print(f"EARNINGS CALL ANALYSIS SUMMARY")
        print(f"Company: {results.company_name} | Quarter: {results.quarter} {results.year}")
        print("="*80)
        
        print("\n📊 OVERALL METRICS")
        print("-" * 80)
        print(f"Sentiment:           {results.overall_sentiment.hybrid_label} ({results.overall_sentiment.hybrid_sentiment_score:.2f})")
        print(f"Complexity:          {results.overall_complexity.complexity_level} ({results.overall_complexity.composite_score:.0f}/100)")
        print(f"Numerical Transparency: {results.overall_numerical.numeric_transparency_score:.2f}% ({results.overall_numerical.vs_sp500_benchmark} S&P 500)")
        print(f"Word Count:          {results.word_count:,}")
        
        if results.red_flags:
            print("\n🚩 RED FLAGS")
            print("-" * 80)
            for flag in results.red_flags:
                print(f"  • {flag}")
        
        if results.strengths:
            print("\n✓ STRENGTHS")
            print("-" * 80)
            for strength in results.strengths:
                print(f"  • {strength}")
        
        if results.key_findings:
            print("\n💡 KEY FINDINGS")
            print("-" * 80)
            for finding in results.key_findings:
                print(f"  • {finding}")
        
        print("\n" + "="*80)

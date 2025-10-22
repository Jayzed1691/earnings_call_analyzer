"""
Main Analysis Aggregator - Phase 2 Enhanced
Combines all analysis modules including deception detection
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import json
import logging
from pathlib import Path
from datetime import datetime

from src.core.transcript_processor import TranscriptProcessor, ProcessedTranscript
from src.analysis.sentiment.hybrid_scorer import HybridSentimentAnalyzer, HybridSentimentScores
from src.analysis.complexity.readability import ComplexityAnalyzer, ComplexityScores
from src.analysis.numerical.transparency import NumericalAnalyzer, NumericalScores

# Phase 2A: Deception Detection Imports
from src.analysis.deception.detector import DeceptionRiskAnalyzer, DeceptionRiskScore
from src.analysis.deception.evasiveness import EvasivenessAnalyzer, EvasivenessScores
from src.analysis.deception.question_evasion import QuestionEvasionDetector, QuestionResponse

# Phase 2B: Sentence-Level Numeric Density Imports
from src.analysis.numerical.sentence_density import (
    SentenceLevelDensityAnalyzer,
    SentenceDensityMetrics,
    DistributionPattern,
    InformativenessMetrics
)

from config.settings import settings
from config.logging_config import PerformanceLogger

# Module logger
logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveAnalysisResult:
    """Complete analysis results for a transcript - Phase 2 Enhanced"""
    # Metadata
    timestamp: str
    company_name: str
    quarter: str
    year: int
    
    # Phase 1: Overall metrics
    overall_sentiment: HybridSentimentScores
    overall_complexity: ComplexityScores
    overall_numerical: NumericalScores
    
    # Phase 1: Section-specific metrics
    prepared_remarks_sentiment: HybridSentimentScores
    qa_sentiment: HybridSentimentScores
    prepared_remarks_complexity: ComplexityScores
    qa_complexity: ComplexityScores
    
    # Phase 1: Speaker-specific metrics (top 2: CEO, CFO)
    ceo_metrics: Dict[str, Any]
    cfo_metrics: Dict[str, Any]
    
    # Phase 2A: Deception Detection
    deception_risk: Optional[DeceptionRiskScore] = None
    evasiveness_scores: Optional[EvasivenessScores] = None
    qa_analysis: Optional[List[QuestionResponse]] = None

    # Phase 2B: Sentence-Level Numeric Density
    sentence_density_metrics: Optional[SentenceDensityMetrics] = None
    distribution_patterns: Optional[DistributionPattern] = None
    informativeness_metrics: Optional[InformativenessMetrics] = None

    # Key insights
    key_findings: List[str]
    red_flags: List[str]
    strengths: List[str]

    # Raw transcript info
    word_count: int
    sentence_count: int


class EarningsCallAnalyzer:
    """Main analyzer that orchestrates all analysis modules including deception detection"""
    
    def __init__(
        self, 
        use_llm_features: bool = True,
        enable_deception_analysis: bool = True
    ):
        """
        Initialize main analyzer
        
        Args:
            use_llm_features: Whether to use LLM-based features (slower but more accurate)
            enable_deception_analysis: Whether to enable Phase 2A deception detection
        """
        logger.info("Initializing Earnings Call Analyzer...")

        # Phase 1 analyzers
        self.transcript_processor = TranscriptProcessor()
        self.sentiment_analyzer = HybridSentimentAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.numerical_analyzer = NumericalAnalyzer(use_llm_contextualization=use_llm_features)
        self.use_llm = use_llm_features

        # Phase 2B: Sentence-level density analyzer
        self.sentence_density_analyzer = SentenceLevelDensityAnalyzer()
        logger.info("Sentence-level density analyzer initialized")

        # Phase 2A: Deception analyzers
        self.enable_deception = enable_deception_analysis and settings.ENABLE_DECEPTION_ANALYSIS

        if self.enable_deception:
            logger.info("Initializing deception detection modules...")
            self.deception_analyzer = DeceptionRiskAnalyzer()
            self.evasiveness_analyzer = EvasivenessAnalyzer()
            self.qa_detector = QuestionEvasionDetector()
            logger.info("Deception detection enabled")
        else:
            logger.info("Deception detection disabled")
            self.deception_analyzer = None
            self.evasiveness_analyzer = None
            self.qa_detector = None

        logger.info("Analyzer initialization complete")
    
    def analyze_transcript(self, file_path: str) -> ComprehensiveAnalysisResult:
        """
        Perform complete analysis on a transcript (Phase 1 + Phase 2A)
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            ComprehensiveAnalysisResult object
        """
        logger.info("="*80)
        logger.info(f"Processing transcript: {file_path}")
        logger.info("="*80)

        # Step 1: Process transcript
        logger.info("STEP 1: TRANSCRIPT PREPROCESSING")
        with PerformanceLogger("transcript_preprocessing", logger):
            logger.info("Preprocessing text...")
            transcript = self.transcript_processor.process(file_path)

            # Validate
            warnings = self.transcript_processor.validate_transcript(transcript)
            if warnings:
                logger.warning("Validation warnings detected:")
                for warning in warnings:
                    logger.warning(f"  - {warning}")
            logger.info(f"Processed {transcript.word_count:,} words in {transcript.sentence_count} sentences")

        # Step 2: Phase 1 Analysis
        logger.info("STEP 2: PHASE 1 CORE ANALYSIS")

        with PerformanceLogger("sentiment_analysis", logger):
            logger.info("Analyzing overall sentiment...")
            overall_sentiment = self.sentiment_analyzer.analyze(transcript.cleaned_text)

        with PerformanceLogger("complexity_analysis", logger):
            logger.info("Analyzing language complexity...")
            overall_complexity = self.complexity_analyzer.analyze(transcript.cleaned_text)

        with PerformanceLogger("numerical_analysis", logger):
            logger.info("Analyzing numerical content...")
            overall_numerical = self.numerical_analyzer.analyze(transcript.cleaned_text)

        # Step 3: Section analysis
        with PerformanceLogger("section_analysis", logger):
            logger.info("Analyzing sections (Prepared Remarks vs Q&A)...")
            section_sentiment = self.sentiment_analyzer.analyze_by_section(transcript.sections)
            section_complexity = self.complexity_analyzer.analyze_by_section(transcript.sections)

        # Step 4: Speaker analysis
        with PerformanceLogger("speaker_analysis", logger):
            logger.info("Analyzing speakers...")
            speaker_sentiment = self.sentiment_analyzer.analyze_by_speaker(transcript.speakers)
            speaker_complexity = self.complexity_analyzer.analyze_by_speaker(transcript.speakers)
            speaker_numerical = self.numerical_analyzer.analyze_by_speaker(transcript.speakers)

        logger.info("Phase 1 analysis complete")
        
        # Step 5: Phase 2A Deception Analysis
        deception_risk = None
        evasiveness_scores = None
        qa_analysis = None
        
        if self.enable_deception:
            logger.info("STEP 3: PHASE 2A DECEPTION ANALYSIS")

            with PerformanceLogger("deception_risk_analysis", logger):
                logger.info("Analyzing deception risk indicators...")
                deception_risk = self.deception_analyzer.analyze(
                    transcript=transcript,
                    sentiment_scores=overall_sentiment,
                    complexity_scores=overall_complexity,
                    numerical_scores=overall_numerical,
                    section_analysis={
                        'prepared_remarks': section_complexity.get('prepared_remarks'),
                        'qa': section_complexity.get('qa')
                    }
                )

            with PerformanceLogger("evasiveness_analysis", logger):
                logger.info("Analyzing evasiveness patterns...")
                evasiveness_scores = self.evasiveness_analyzer.analyze(transcript.cleaned_text)

            # Q&A analysis (if Q&A section exists)
            if transcript.sections.get('qa') and settings.ENABLE_QA_ANALYSIS:
                with PerformanceLogger("qa_evasion_analysis", logger):
                    logger.info("Analyzing Q&A exchanges for evasion...")
                    qa_analysis = self.qa_detector.analyze_qa_section(transcript.sections['qa'])
                    logger.info(f"Analyzed {len(qa_analysis)} Q&A pairs")
            else:
                logger.info("No Q&A section found, skipping Q&A analysis")
                qa_analysis = None

            logger.info("Deception analysis complete")

        # Step 5.5: Phase 2B Sentence-Level Numeric Density Analysis
        logger.info("STEP 3.5: PHASE 2B SENTENCE-LEVEL DENSITY ANALYSIS")
        sentence_density_metrics = None
        distribution_patterns = None
        informativeness_metrics = None

        with PerformanceLogger("sentence_density_analysis", logger):
            logger.info("Analyzing sentence-level numeric density...")
            sentence_density_metrics = self.sentence_density_analyzer.analyze_sentence_density(
                transcript.cleaned_text
            )
            logger.info(f"Analyzed {sentence_density_metrics.total_sentences} sentences")
            logger.info(f"Dense sentences: {sentence_density_metrics.numeric_dense_sentences} ({sentence_density_metrics.proportion_numeric_dense:.1%})")

        with PerformanceLogger("distribution_pattern_analysis", logger):
            logger.info("Analyzing numeric distribution patterns...")
            distribution_patterns = self.sentence_density_analyzer.analyze_distribution_patterns(
                sentence_density_metrics,
                sections=transcript.sections,
                speakers=transcript.speakers
            )
            logger.info(f"Pattern: {distribution_patterns.pattern_type} (confidence: {distribution_patterns.pattern_confidence:.1%})")
            logger.info(f"Clusters detected: {distribution_patterns.cluster_count}")

        with PerformanceLogger("informativeness_calculation", logger):
            logger.info("Calculating informativeness metrics...")
            informativeness_metrics = self.sentence_density_analyzer.calculate_informativeness(
                sentence_density_metrics,
                overall_numerical,
                distribution_patterns
            )
            logger.info(f"NIR: {informativeness_metrics.numeric_inclusion_ratio:.2%}")
            logger.info(f"Informativeness: {informativeness_metrics.informativeness_score:.1f}/100")
            logger.info(f"Forecast Relevance: {informativeness_metrics.forecast_relevance_score:.1f}/100")

        logger.info("Sentence-level density analysis complete")

        # Step 6: Generate insights
        logger.info("STEP 4: GENERATING INSIGHTS")
        with PerformanceLogger("insights_generation", logger):
            logger.info("Identifying patterns and generating insights...")
            key_findings, red_flags, strengths = self._generate_insights(
                overall_sentiment,
                overall_complexity,
                overall_numerical,
                section_sentiment,
                section_complexity,
                deception_risk,
                evasiveness_scores,
                qa_analysis
            )

            logger.info(f"Generated {len(key_findings)} findings, {len(red_flags)} red flags, {len(strengths)} strengths")
        
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
            deception_risk=deception_risk,
            evasiveness_scores=evasiveness_scores,
            qa_analysis=qa_analysis,
            sentence_density_metrics=sentence_density_metrics,
            distribution_patterns=distribution_patterns,
            informativeness_metrics=informativeness_metrics,
            key_findings=key_findings,
            red_flags=red_flags,
            strengths=strengths,
            word_count=transcript.word_count,
            sentence_count=transcript.sentence_count
        )
        
        logger.info("="*80)
        logger.info("ANALYSIS COMPLETE!")
        logger.info("="*80)

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
        section_complexity: Dict,
        deception_risk: Optional[DeceptionRiskScore] = None,
        evasiveness_scores: Optional[EvasivenessScores] = None,
        qa_analysis: Optional[List[QuestionResponse]] = None
    ) -> tuple:
        """
        Generate key findings, red flags, and strengths
        Phase 2 Enhanced - includes deception insights
        
        Returns:
            Tuple of (key_findings, red_flags, strengths)
        """
        key_findings = []
        red_flags = []
        strengths = []
        
        # ===== PHASE 1: SENTIMENT INSIGHTS =====
        if overall_sentiment.hybrid_sentiment_score > 0.3:
            key_findings.append(f"Strong positive sentiment (score: {overall_sentiment.hybrid_sentiment_score:.2f})")
            strengths.append("Optimistic tone throughout the call")
        elif overall_sentiment.hybrid_sentiment_score < -0.3:
            key_findings.append(f"Negative sentiment (score: {overall_sentiment.hybrid_sentiment_score:.2f})")
            red_flags.append("Pessimistic or defensive language detected")
        
        # ===== PHASE 1: COMPLEXITY INSIGHTS =====
        if overall_complexity.composite_score > 70:
            key_findings.append(f"High language complexity ({overall_complexity.complexity_level})")
            red_flags.append(f"Language complexity score of {overall_complexity.composite_score:.0f} may indicate obfuscation")
        elif overall_complexity.composite_score < 40:
            strengths.append("Clear, accessible language")
        
        # ===== PHASE 1: NUMERICAL TRANSPARENCY INSIGHTS =====
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
        
        # ===== PHASE 1: SECTION COMPARISONS =====
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
        
        # ===== PHASE 2A: DECEPTION RISK INSIGHTS =====
        if deception_risk:
            key_findings.append(f"Deception risk assessment: {deception_risk.risk_level} ({deception_risk.overall_risk_score:.0f}/100)")
            
            # Overall risk level alerts
            if deception_risk.risk_level == "Critical":
                red_flags.append(f"⚠️ CRITICAL DECEPTION RISK: Score of {deception_risk.overall_risk_score:.0f}/100")
            elif deception_risk.risk_level == "High":
                red_flags.append(f"⚠️ HIGH DECEPTION RISK: Score of {deception_risk.overall_risk_score:.0f}/100")
            elif deception_risk.risk_level == "Low":
                strengths.append(f"Low deception risk indicators (score: {deception_risk.overall_risk_score:.0f}/100)")
            
            # Specific indicator alerts
            indicators = deception_risk.indicators
            
            if indicators.hedging_score > settings.HEDGING_DENSITY_THRESHOLD:
                red_flags.append(f"Excessive hedging language ({indicators.hedging_score:.1f}%)")
            
            if indicators.qualifier_density > settings.QUALIFIER_DENSITY_THRESHOLD:
                red_flags.append(f"High qualifier density ({indicators.qualifier_density:.1f}%)")
            
            if indicators.passive_voice_ratio > settings.PASSIVE_VOICE_THRESHOLD:
                red_flags.append(f"High passive voice usage ({indicators.passive_voice_ratio:.1f}%)")
            
            if indicators.complexity_spike_qa > 60:
                red_flags.append("Significant complexity spike in Q&A responses")
            
            if indicators.forward_avoidance > 70:
                red_flags.append("Avoidance of forward-looking numbers")
            
            # Add top triggered flags
            if deception_risk.triggered_flags:
                for flag in deception_risk.triggered_flags[:3]:  # Top 3
                    if flag not in red_flags:  # Avoid duplicates
                        red_flags.append(flag)
        
        # ===== PHASE 2A: EVASIVENESS INSIGHTS =====
        if evasiveness_scores:
            key_findings.append(f"Evasiveness level: {evasiveness_scores.evasiveness_level} ({evasiveness_scores.overall_evasiveness:.1f})")
            
            if evasiveness_scores.vs_baseline == "above":
                red_flags.append(f"Above-average evasiveness ({evasiveness_scores.overall_evasiveness:.1f} vs {settings.SP500_EVASIVENESS_BASELINE} baseline)")
            elif evasiveness_scores.vs_baseline == "below":
                strengths.append(f"Below-average evasiveness ({evasiveness_scores.overall_evasiveness:.1f} vs {settings.SP500_EVASIVENESS_BASELINE} baseline)")
        
        # ===== PHASE 2A: Q&A EVASION INSIGHTS =====
        if qa_analysis:
            evasive_count = sum(1 for qa in qa_analysis if qa.is_evasive)
            evasion_rate = (evasive_count / len(qa_analysis)) * 100 if qa_analysis else 0
            
            key_findings.append(f"Q&A evasion rate: {evasion_rate:.1f}% ({evasive_count}/{len(qa_analysis)} questions)")
            
            if evasion_rate > settings.QUESTION_AVOIDANCE_ALERT:
                red_flags.append(f"High question evasion rate: {evasion_rate:.1f}% of analyst questions evaded")
            elif evasion_rate < 20:
                strengths.append("Direct and responsive answers to analyst questions")
        
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
            json.dump(results_dict, f, indent=2, default=str)

        logger.info(f"Results saved to: {output_path}")
    
    def print_summary(self, results: ComprehensiveAnalysisResult) -> None:
        """Print a human-readable summary of results - Phase 2 Enhanced"""
        print("\n" + "="*80)
        print(f"EARNINGS CALL ANALYSIS SUMMARY - PHASE 2")
        print(f"Company: {results.company_name} | Quarter: {results.quarter} {results.year}")
        print(f"Analysis Date: {results.timestamp.split('T')[0]}")
        print("="*80)
        
        # ===== PHASE 1: CORE METRICS =====
        print("\n📊 PHASE 1: CORE METRICS")
        print("-" * 80)
        print(f"Sentiment:              {results.overall_sentiment.hybrid_label} ({results.overall_sentiment.hybrid_sentiment_score:.2f})")
        print(f"Complexity:             {results.overall_complexity.complexity_level} ({results.overall_complexity.composite_score:.0f}/100)")
        print(f"Numerical Transparency: {results.overall_numerical.numeric_transparency_score:.2f}% ({results.overall_numerical.vs_sp500_benchmark} S&P 500)")
        print(f"Word Count:             {results.word_count:,}")
        
        # ===== PHASE 2A: DECEPTION METRICS =====
        if results.deception_risk:
            print("\n🔍 PHASE 2A: DECEPTION RISK ASSESSMENT")
            print("-" * 80)
            risk = results.deception_risk
            
            # Risk level with color coding
            risk_emoji = {
                "Low": "✅",
                "Moderate": "⚠️",
                "High": "🚨",
                "Critical": "🔴"
            }
            emoji = risk_emoji.get(risk.risk_level, "❓")
            
            print(f"Overall Risk:           {emoji} {risk.risk_level} ({risk.overall_risk_score:.0f}/100)")
            print(f"Confidence:             {risk.confidence:.0%}")
            
            # Component scores
            print(f"\nRisk Components:")
            print(f"  • Linguistic:         {risk.risk_components['linguistic']:.1f}/100")
            print(f"  • Behavioral:         {risk.risk_components['behavioral']:.1f}/100")
            print(f"  • Numerical:          {risk.risk_components['numerical']:.1f}/100")
            print(f"  • Evasion:            {risk.risk_components['evasion']:.1f}/100")
            
            # Top indicators
            indicators = risk.indicators
            print(f"\nKey Indicators:")
            print(f"  • Hedging Density:    {indicators.hedging_score:.1f}%")
            print(f"  • Qualifier Density:  {indicators.qualifier_density:.1f}%")
            print(f"  • Passive Voice:      {indicators.passive_voice_ratio:.1f}%")
            print(f"  • Forward Avoidance:  {indicators.forward_avoidance:.1f}/100")
            
            if risk.triggered_flags:
                print(f"\nTriggered Flags ({len(risk.triggered_flags)}):")
                for flag in risk.triggered_flags[:5]:  # Show top 5
                    print(f"  • {flag}")
        
        # Evasiveness scores
        if results.evasiveness_scores:
            print("\n📝 EVASIVENESS ANALYSIS")
            print("-" * 80)
            ev = results.evasiveness_scores
            print(f"Overall Evasiveness:    {ev.evasiveness_level} ({ev.overall_evasiveness:.1f})")
            print(f"vs S&P 500 Baseline:    {ev.vs_baseline} ({settings.SP500_EVASIVENESS_BASELINE})")
            print(f"  • Qualifiers:         {ev.qualifier_density:.1f}%")
            print(f"  • Hedging:            {ev.hedging_language_pct:.1f}%")
            print(f"  • Passive Voice:      {ev.passive_voice_pct:.1f}%")
        
        # Q&A analysis
        if results.qa_analysis:
            print("\n💬 Q&A ANALYSIS")
            print("-" * 80)
            total_qa = len(results.qa_analysis)
            evasive = sum(1 for qa in results.qa_analysis if qa.is_evasive)
            evasion_rate = (evasive / total_qa * 100) if total_qa > 0 else 0

            print(f"Total Q&A Pairs:        {total_qa}")
            print(f"Evasive Responses:      {evasive} ({evasion_rate:.1f}%)")

            if evasive > 0:
                print(f"\nMost Evasive Questions:")
                sorted_qa = sorted(results.qa_analysis, key=lambda x: x.response_relevance)
                for i, qa in enumerate(sorted_qa[:3], 1):
                    print(f"  {i}. Relevance: {qa.response_relevance:.2f} | Type: {qa.evasion_type}")
                    print(f"     Q: {qa.question[:100]}...")

        # ===== PHASE 2B: SENTENCE-LEVEL DENSITY =====
        if results.sentence_density_metrics:
            print("\n📈 PHASE 2B: SENTENCE-LEVEL NUMERIC DENSITY")
            print("-" * 80)
            sdm = results.sentence_density_metrics

            # Sentence classification
            print(f"Sentence Classification:")
            print(f"  • Total Sentences:    {sdm.total_sentences}")
            print(f"  • Dense (>10%):       {sdm.numeric_dense_sentences} ({sdm.proportion_numeric_dense:.1%})")
            print(f"  • Moderate (5-10%):   {sdm.numeric_moderate_sentences}")
            print(f"  • Sparse (1-5%):      {sdm.numeric_sparse_sentences}")
            print(f"  • Narrative (0%):     {sdm.narrative_sentences} ({sdm.proportion_narrative:.1%})")

            # Statistics
            print(f"\nDensity Statistics:")
            print(f"  • Mean:               {sdm.mean_numeric_density:.2f}%")
            print(f"  • Median:             {sdm.median_numeric_density:.2f}%")
            print(f"  • Std Dev:            {sdm.std_numeric_density:.2f}%")
            print(f"  • Max:                {sdm.max_numeric_density:.2f}%")

            # Top dense sentences
            if sdm.top_dense_sentences:
                print(f"\nTop 3 Most Numeric Sentences:")
                for i, (sentence, density) in enumerate(sdm.top_dense_sentences[:3], 1):
                    preview = sentence.strip()[:65] + "..." if len(sentence.strip()) > 65 else sentence.strip()
                    print(f"  {i}. [{density:.1f}%] {preview}")

        # Distribution patterns
        if results.distribution_patterns:
            print("\n📊 DISTRIBUTION PATTERNS")
            print("-" * 80)
            dp = results.distribution_patterns

            print(f"Pattern Type:           {dp.pattern_type.upper()} (confidence: {dp.pattern_confidence:.1%})")
            print(f"Clusters Detected:      {dp.cluster_count}")
            print(f"\nPositional Density:")
            print(f"  • Beginning (20%):    {dp.beginning_density:.2f}%")
            print(f"  • Middle (60%):       {dp.middle_density:.2f}%")
            print(f"  • End (20%):          {dp.end_density:.2f}%")

            if dp.qa_density_differential != 0.0:
                print(f"\nQ&A Differential:")
                print(f"  • Questions:          {dp.question_avg_density:.2f}%")
                print(f"  • Answers:            {dp.answer_avg_density:.2f}%")
                diff_dir = "higher" if dp.qa_density_differential > 0 else "lower"
                print(f"  • Differential:       {abs(dp.qa_density_differential):.2f}% ({diff_dir} in answers)")

        # Informativeness metrics
        if results.informativeness_metrics:
            print("\n💡 INFORMATIVENESS METRICS")
            print("-" * 80)
            im = results.informativeness_metrics

            print(f"Numeric Inclusion Ratio: {im.numeric_inclusion_ratio:.2%}")
            print(f"Informativeness Score:   {im.informativeness_score:.1f}/100 ({im.quantitative_disclosure_level})")
            print(f"Forecast Relevance:      {im.forecast_relevance_score:.1f}/100")
            print(f"Transparency Tier:       {im.transparency_tier.replace('_', ' ').title()}")
            print(f"\nRisk Signals:")
            print(f"  • Numeric Avoidance:  {im.numeric_avoidance_risk:.1f}/100")
            print(f"  • Vagueness Penalty:  {im.vagueness_penalty:.1f}/100")

        # ASCII Heatmap
        if results.distribution_patterns and results.sentence_density_metrics:
            print("\n🔥 NUMERIC DENSITY HEATMAP")
            print("-" * 80)
            heatmap = self.sentence_density_analyzer.generate_ascii_heatmap(
                results.distribution_patterns,
                results.sentence_density_metrics
            )
            print(heatmap)

        # ===== RED FLAGS =====
        if results.red_flags:
            print("\n🚩 RED FLAGS")
            print("-" * 80)
            for flag in results.red_flags:
                print(f"  • {flag}")
        
        # ===== STRENGTHS =====
        if results.strengths:
            print("\n✅ STRENGTHS")
            print("-" * 80)
            for strength in results.strengths:
                print(f"  • {strength}")
        
        # ===== KEY FINDINGS =====
        if results.key_findings:
            print("\n💡 KEY FINDINGS")
            print("-" * 80)
            for finding in results.key_findings:
                print(f"  • {finding}")
        
        print("\n" + "="*80)
        
        # Summary recommendation
        if results.deception_risk:
            risk_level = results.deception_risk.risk_level
            if risk_level in ["High", "Critical"]:
                print("\n⚠️  RECOMMENDATION: This transcript exhibits concerning patterns.")
                print("    Further investigation and corroboration with financial data is advised.")
            elif risk_level == "Moderate":
                print("\n💡 RECOMMENDATION: Monitor for consistency with financial performance.")
            else:
                print("\n✅ RECOMMENDATION: Communication patterns appear transparent.")
            print("="*80)

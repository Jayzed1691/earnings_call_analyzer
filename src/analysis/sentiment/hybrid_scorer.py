"""
Hybrid Sentiment Analysis - Combines Lexicon and LLM approaches
"""
from dataclasses import dataclass
from typing import Dict
from src.analysis.sentiment.lexicon_analyzer import LexiconSentimentAnalyzer, LMSentimentScores
from src.analysis.sentiment.llm_analyzer import LLMSentimentAnalyzer, LLMSentimentScores
from config.settings import settings


@dataclass
class HybridSentimentScores:
    """Combined sentiment scores from lexicon and LLM"""
    # Lexicon scores
    lexicon_scores: LMSentimentScores
    
    # LLM scores
    llm_scores: LLMSentimentScores
    
    # Hybrid scores
    hybrid_sentiment_score: float  # Weighted combination
    hybrid_label: str  # Positive, Negative, Neutral
    
    # Meta information
    word_count: int
    confidence: float


class HybridSentimentAnalyzer:
    """
    Combines Loughran-McDonald lexicon with LLM-based contextual analysis
    Implements 70% LLM / 30% Lexicon weighting as specified in PRD
    """
    
    def __init__(self):
        """Initialize hybrid analyzer"""
        self.lexicon_analyzer = LexiconSentimentAnalyzer()
        self.llm_analyzer = LLMSentimentAnalyzer()
        
        # Weighting from PRD
        self.lexicon_weight = settings.HYBRID_SENTIMENT_WEIGHT_LEXICON  # 0.3
        self.llm_weight = settings.HYBRID_SENTIMENT_WEIGHT_LLM  # 0.7
    
    def analyze(self, text: str) -> HybridSentimentScores:
        """
        Perform hybrid sentiment analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            HybridSentimentScores object
        """
        # Get lexicon-based scores
        lexicon_scores = self.lexicon_analyzer.analyze(text)
        
        # Get LLM-based scores
        llm_scores = self.llm_analyzer.analyze(text)
        
        # Calculate hybrid score
        # Lexicon: Net Positivity ranges from -100 to +100
        # LLM: sentiment_score ranges from -1.0 to +1.0
        # Normalize lexicon to same scale as LLM
        normalized_lexicon = lexicon_scores.net_positivity / 100.0
        
        hybrid_score = (
            self.lexicon_weight * normalized_lexicon +
            self.llm_weight * llm_scores.sentiment_score
        )
        
        # Determine hybrid label
        if hybrid_score > 0.2:
            hybrid_label = "Positive"
        elif hybrid_score < -0.2:
            hybrid_label = "Negative"
        else:
            hybrid_label = "Neutral"
        
        return HybridSentimentScores(
            lexicon_scores=lexicon_scores,
            llm_scores=llm_scores,
            hybrid_sentiment_score=hybrid_score,
            hybrid_label=hybrid_label,
            word_count=lexicon_scores.word_count,
            confidence=llm_scores.confidence
        )
    
    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, HybridSentimentScores]:
        """
        Analyze sentiment for each section
        
        Args:
            sections: Dict of section_name -> text
            
        Returns:
            Dict of section_name -> HybridSentimentScores
        """
        results = {}
        
        for section_name, text in sections.items():
            if text.strip():
                results[section_name] = self.analyze(text)
        
        return results
    
    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, HybridSentimentScores]:
        """
        Analyze sentiment for each speaker
        
        Args:
            speakers: Dict of speaker_name -> text
            
        Returns:
            Dict of speaker_name -> HybridSentimentScores
        """
        results = {}
        
        for speaker_name, text in speakers.items():
            if text.strip():
                results[speaker_name] = self.analyze(text)
        
        return results
    
    def compare_approaches(self, text: str) -> Dict[str, any]:
        """
        Compare lexicon vs LLM vs hybrid approaches
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with comparison metrics
        """
        scores = self.analyze(text)
        
        return {
            'lexicon_net_positivity': scores.lexicon_scores.net_positivity,
            'llm_sentiment_score': scores.llm_scores.sentiment_score,
            'hybrid_sentiment_score': scores.hybrid_sentiment_score,
            'lexicon_label': self._score_to_label(scores.lexicon_scores.net_positivity / 100),
            'llm_label': scores.llm_scores.overall_sentiment,
            'hybrid_label': scores.hybrid_label,
            'agreement': self._check_agreement(scores),
        }
    
    def _score_to_label(self, score: float) -> str:
        """Convert numerical score to label"""
        if score > 0.2:
            return "Positive"
        elif score < -0.2:
            return "Negative"
        else:
            return "Neutral"
    
    def _check_agreement(self, scores: HybridSentimentScores) -> str:
        """Check if lexicon and LLM agree on sentiment"""
        lexicon_label = self._score_to_label(scores.lexicon_scores.net_positivity / 100)
        llm_label = scores.llm_scores.overall_sentiment
        
        if lexicon_label == llm_label:
            return "Strong Agreement"
        elif (lexicon_label == "Neutral" or llm_label == "Neutral"):
            return "Partial Agreement"
        else:
            return "Disagreement"

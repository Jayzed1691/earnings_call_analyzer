"""
LLM-based contextual sentiment analysis using Ollama
Enhanced with result caching for performance
"""
from typing import Dict, List
from dataclasses import dataclass, asdict
import logging
import numpy as np
from src.models.ollama_client import ollama_client
from src.utils.text_utils import split_into_chunks, tokenize_sentences
from src.cache.result_cache import get_cache
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMSentimentScores:
    """LLM-based sentiment scores"""
    overall_sentiment: str  # Positive, Negative, Neutral
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    segment_sentiments: List[Dict[str, any]]  # Individual segment results


class LLMSentimentAnalyzer:
    """Contextual sentiment analysis using Ollama LLM with caching"""

    def __init__(self, use_cache: bool = True):
        """
        Initialize LLM analyzer

        Args:
            use_cache: Whether to use result caching (default: True)
        """
        self.client = ollama_client
        self.sentiment_map = {
            "Positive": 1.0,
            "Negative": -1.0,
            "Neutral": 0.0
        }
        self.cache = get_cache() if use_cache else None
    
    def analyze(self, text: str, use_chunks: bool = True) -> LLMSentimentScores:
        """
        Analyze sentiment using LLM with caching

        Args:
            text: Text to analyze
            use_chunks: Whether to chunk long text

        Returns:
            LLMSentimentScores object
        """
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(text, 'llm_sentiment')
            if cached_result is not None:
                return LLMSentimentScores(**cached_result)

        # Perform analysis
        if use_chunks and len(text.split()) > settings.LLM_CHUNK_SIZE:
            # Process in chunks for long text
            result = self._analyze_chunked(text)
        else:
            # Process as single segment
            llm_result = self.client.analyze_sentiment(text)
            sentiment_score = self.sentiment_map.get(llm_result['sentiment'], 0.0)

            result = LLMSentimentScores(
                overall_sentiment=llm_result['sentiment'],
                sentiment_score=sentiment_score,
                confidence=llm_result['confidence'],
                segment_sentiments=[llm_result]
            )

        # Cache the result
        if self.cache:
            self.cache.set(text, 'llm_sentiment', asdict(result))

        return result
    
    def _analyze_chunked(self, text: str) -> LLMSentimentScores:
        """
        Analyze text in chunks and aggregate results
        
        Args:
            text: Text to analyze
            
        Returns:
            Aggregated LLMSentimentScores
        """
        chunks = split_into_chunks(
            text,
            chunk_size=settings.LLM_CHUNK_SIZE,
            overlap=settings.LLM_CHUNK_OVERLAP
        )
        
        segment_results = []
        sentiment_scores = []
        confidences = []
        
        for i, chunk in enumerate(chunks):
            try:
                result = self.client.analyze_sentiment(chunk)
                segment_results.append(result)
                
                # Convert sentiment to numerical score
                score = self.sentiment_map.get(result['sentiment'], 0.0)
                sentiment_scores.append(score)
                confidences.append(result['confidence'])
                
            except Exception as e:
                logger.warning(f"Failed to analyze chunk {i}: {str(e)}")
                # Add neutral default
                segment_results.append({
                    'sentiment': 'Neutral',
                    'confidence': 0.5,
                    'reasoning': f'Failed to analyze: {str(e)}'
                })
                sentiment_scores.append(0.0)
                confidences.append(0.5)
        
        # Aggregate with confidence weighting
        if sentiment_scores:
            weighted_score = np.average(sentiment_scores, weights=confidences)
            avg_confidence = np.mean(confidences)
            
            # Determine overall sentiment from weighted score
            if weighted_score > 0.2:
                overall_sentiment = "Positive"
            elif weighted_score < -0.2:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"
        else:
            weighted_score = 0.0
            avg_confidence = 0.5
            overall_sentiment = "Neutral"
        
        return LLMSentimentScores(
            overall_sentiment=overall_sentiment,
            sentiment_score=weighted_score,
            confidence=avg_confidence,
            segment_sentiments=segment_results
        )
    
    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, LLMSentimentScores]:
        """
        Analyze sentiment for each section
        
        Args:
            sections: Dict of section_name -> text
            
        Returns:
            Dict of section_name -> LLMSentimentScores
        """
        results = {}
        
        for section_name, text in sections.items():
            if text.strip():  # Skip empty sections
                results[section_name] = self.analyze(text)
        
        return results
    
    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, LLMSentimentScores]:
        """
        Analyze sentiment for each speaker
        
        Args:
            speakers: Dict of speaker_name -> text
            
        Returns:
            Dict of speaker_name -> LLMSentimentScores
        """
        results = {}
        
        for speaker_name, text in speakers.items():
            if text.strip():  # Skip empty speakers
                results[speaker_name] = self.analyze(text)
        
        return results
    
    def analyze_sentences(self, text: str) -> List[Dict[str, any]]:
        """
        Analyze sentiment at sentence level
        
        Args:
            text: Text to analyze
            
        Returns:
            List of sentence-level sentiment results
        """
        sentences = tokenize_sentences(text)
        sentence_results = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) < 5:  # Skip very short sentences
                continue
            
            try:
                result = self.client.analyze_sentiment(sentence)
                result['sentence'] = sentence
                result['index'] = i
                sentence_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to analyze sentence {i}: {str(e)}")
        
        return sentence_results

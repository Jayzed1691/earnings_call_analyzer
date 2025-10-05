"""
Loughran-McDonald Dictionary-Based Sentiment Analysis
"""
from typing import Dict, List, Set
from pathlib import Path
from dataclasses import dataclass
from src.utils.text_utils import tokenize_words
from config.settings import settings


@dataclass
class LMSentimentScores:
    """Loughran-McDonald sentiment scores"""
    negative: float
    positive: float
    uncertainty: float
    litigious: float
    strong_modal: float
    weak_modal: float
    constraining: float
    net_positivity: float
    word_count: int
    
    # Raw counts
    negative_count: int = 0
    positive_count: int = 0
    uncertainty_count: int = 0
    litigious_count: int = 0
    strong_modal_count: int = 0
    weak_modal_count: int = 0
    constraining_count: int = 0


class LMDictionary:
    """Loughran-McDonald Master Dictionary"""
    
    def __init__(self, dict_path: Path = None):
        """
        Initialize LM Dictionary
        
        Args:
            dict_path: Path to dictionary directory
        """
        self.dict_path = dict_path or settings.DICTIONARIES_DIR / "loughran_mcdonald"
        self.dictionaries = self._load_dictionaries()
    
    def _load_dictionaries(self) -> Dict[str, Set[str]]:
        """Load all LM dictionary categories"""
        categories = [
            'negative', 'positive', 'uncertainty', 'litigious',
            'strong_modal', 'weak_modal', 'constraining'
        ]
        
        dictionaries = {}
        
        for category in categories:
            file_path = self.dict_path / f"{category}.txt"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Words are typically one per line in LM dictionary
                    words = set(line.strip().lower() for line in f if line.strip())
                dictionaries[category] = words
            else:
                # Create empty set if file doesn't exist
                dictionaries[category] = set()
                print(f"Warning: {category}.txt not found at {file_path}")
        
        return dictionaries
    
    def get_word_categories(self, word: str) -> List[str]:
        """
        Get all categories a word belongs to
        
        Args:
            word: Word to check
            
        Returns:
            List of category names
        """
        word_lower = word.lower()
        categories = []
        
        for category, word_set in self.dictionaries.items():
            if word_lower in word_set:
                categories.append(category)
        
        return categories


class LexiconSentimentAnalyzer:
    """Loughran-McDonald lexicon-based sentiment analyzer"""
    
    def __init__(self):
        """Initialize analyzer with LM dictionary"""
        self.dictionary = LMDictionary()
    
    def analyze(self, text: str) -> LMSentimentScores:
        """
        Analyze sentiment using LM dictionary
        
        Args:
            text: Text to analyze
            
        Returns:
            LMSentimentScores object
        """
        # Tokenize text
        words = tokenize_words(text, lowercase=True, remove_punct=True)
        word_count = len(words)
        
        if word_count == 0:
            return self._empty_scores()
        
        # Count words in each category
        counts = {
            'negative': 0,
            'positive': 0,
            'uncertainty': 0,
            'litigious': 0,
            'strong_modal': 0,
            'weak_modal': 0,
            'constraining': 0,
        }
        
        for word in words:
            categories = self.dictionary.get_word_categories(word)
            for category in categories:
                counts[category] += 1
        
        # Calculate percentage scores
        scores = {
            category: (count / word_count) * 100
            for category, count in counts.items()
        }
        
        # Calculate net positivity
        if counts['positive'] + counts['negative'] > 0:
            net_positivity = (
                (counts['positive'] - counts['negative']) /
                (counts['positive'] + counts['negative'])
            ) * 100
        else:
            net_positivity = 0.0
        
        return LMSentimentScores(
            negative=scores['negative'],
            positive=scores['positive'],
            uncertainty=scores['uncertainty'],
            litigious=scores['litigious'],
            strong_modal=scores['strong_modal'],
            weak_modal=scores['weak_modal'],
            constraining=scores['constraining'],
            net_positivity=net_positivity,
            word_count=word_count,
            negative_count=counts['negative'],
            positive_count=counts['positive'],
            uncertainty_count=counts['uncertainty'],
            litigious_count=counts['litigious'],
            strong_modal_count=counts['strong_modal'],
            weak_modal_count=counts['weak_modal'],
            constraining_count=counts['constraining'],
        )
    
    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, LMSentimentScores]:
        """
        Analyze sentiment for each section
        
        Args:
            sections: Dict of section_name -> text
            
        Returns:
            Dict of section_name -> LMSentimentScores
        """
        return {
            section_name: self.analyze(text)
            for section_name, text in sections.items()
        }
    
    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, LMSentimentScores]:
        """
        Analyze sentiment for each speaker
        
        Args:
            speakers: Dict of speaker_name -> text
            
        Returns:
            Dict of speaker_name -> LMSentimentScores
        """
        return {
            speaker_name: self.analyze(text)
            for speaker_name, text in speakers.items()
        }
    
    def _empty_scores(self) -> LMSentimentScores:
        """Return empty scores for zero-length text"""
        return LMSentimentScores(
            negative=0.0,
            positive=0.0,
            uncertainty=0.0,
            litigious=0.0,
            strong_modal=0.0,
            weak_modal=0.0,
            constraining=0.0,
            net_positivity=0.0,
            word_count=0,
        )
    
    def get_sentiment_words(self, text: str, category: str) -> List[str]:
        """
        Extract words belonging to a specific sentiment category
        
        Args:
            text: Text to analyze
            category: Sentiment category
            
        Returns:
            List of words in that category
        """
        words = tokenize_words(text, lowercase=True, remove_punct=True)
        category_words = []
        
        for word in words:
            if category in self.dictionary.get_word_categories(word):
                category_words.append(word)
        
        return category_words
    
    def benchmark_comparison(self, scores: LMSentimentScores) -> Dict[str, str]:
        """
        Compare scores to S&P 500 benchmarks
        
        Args:
            scores: Sentiment scores to compare
            
        Returns:
            Dict with comparison indicators
        """
        benchmark_net_pos = settings.SP500_NET_POSITIVITY
        
        comparison = {}
        
        # Net positivity comparison
        if scores.net_positivity > benchmark_net_pos * 1.1:
            comparison['net_positivity'] = "above"
        elif scores.net_positivity < benchmark_net_pos * 0.9:
            comparison['net_positivity'] = "below"
        else:
            comparison['net_positivity'] = "at"
        
        return comparison

"""
Numerical Content Analysis Module
Implements all 4 numerical metrics as specified in PRD
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re
from src.utils.text_utils import (
    extract_numerical_tokens,
    identify_forward_looking_statements,
    identify_backward_looking_statements,
    tokenize_words
)
from src.models.ollama_client import ollama_client
from config.settings import settings


@dataclass
class NumericalScores:
    """Numerical content transparency scores"""
    # Primary metrics
    numeric_transparency_score: float  # Percentage of words that are numbers
    numerical_specificity_index: float  # Average specificity (0.3-2.0)
    forward_looking_density: float  # Numbers in forward statements
    backward_looking_density: float  # Numbers in backward statements
    forward_to_backward_ratio: float  # Ratio of forward to backward
    contextualization_quality_score: float  # 0.0-1.0
    
    # Component counts
    total_numerical_tokens: int
    forward_numerical_tokens: int
    backward_numerical_tokens: int
    well_contextualized_count: int
    undercontextualized_count: int
    
    # Benchmarking
    vs_sp500_benchmark: str  # above, at, below


class NumericalAnalyzer:
    """Analyzes numerical content transparency and quality"""
    
    def __init__(self, use_llm_contextualization: bool = True):
        """
        Initialize numerical analyzer
        
        Args:
            use_llm_contextualization: Whether to use LLM for contextualization
        """
        self.use_llm = use_llm_contextualization
        self.client = ollama_client if use_llm_contextualization else None
        
        # Specificity weights from PRD
        self.specificity_weights = {
            'rounded': 0.5,
            'whole': 1.0,
            'one_decimal': 1.5,
            'two_plus_decimal': 2.0,
            'uncertain': 0.3
        }
    
    def analyze(self, text: str) -> NumericalScores:
        """
        Analyze numerical content
        
        Args:
            text: Text to analyze
            
        Returns:
            NumericalScores object
        """
        # Extract numerical tokens
        numerical_tokens = extract_numerical_tokens(text)
        
        if not numerical_tokens:
            return self._empty_scores()
        
        # Count total words
        words = tokenize_words(text, lowercase=False, remove_punct=True)
        total_words = len(words)
        
        # Calculate transparency score
        transparency_score = (len(numerical_tokens) / total_words) * 100
        
        # Calculate specificity index
        specificity_index = self._calculate_specificity_index(numerical_tokens)
        
        # Calculate forward/backward density
        forward_density, backward_density, fwd_tokens, bwd_tokens = \
            self._calculate_temporal_density(text, numerical_tokens)
        
        # Calculate forward-to-backward ratio
        if backward_density > 0:
            fb_ratio = forward_density / backward_density
        else:
            fb_ratio = 0.0
        
        # Calculate contextualization quality
        context_score, well_context, under_context = \
            self._calculate_contextualization(numerical_tokens)
        
        # Benchmark comparison
        benchmark_status = self._benchmark_comparison(transparency_score)
        
        return NumericalScores(
            numeric_transparency_score=transparency_score,
            numerical_specificity_index=specificity_index,
            forward_looking_density=forward_density,
            backward_looking_density=backward_density,
            forward_to_backward_ratio=fb_ratio,
            contextualization_quality_score=context_score,
            total_numerical_tokens=len(numerical_tokens),
            forward_numerical_tokens=fwd_tokens,
            backward_numerical_tokens=bwd_tokens,
            well_contextualized_count=well_context,
            undercontextualized_count=under_context,
            vs_sp500_benchmark=benchmark_status
        )
    
    def _calculate_specificity_index(self, numerical_tokens: List[Tuple[str, str]]) -> float:
        """
        Calculate numerical specificity index
        
        Args:
            numerical_tokens: List of (number, context) tuples
            
        Returns:
            Average specificity score (0.3-2.0)
        """
        if not numerical_tokens:
            return 0.0
        
        specificity_scores = []
        
        for number, _ in numerical_tokens:
            specificity = self._classify_number_specificity(number)
            specificity_scores.append(specificity)
        
        return sum(specificity_scores) / len(specificity_scores)
    
    def _classify_number_specificity(self, number: str) -> float:
        """Classify a number's specificity"""
        # Remove currency symbols and scale words
        clean_num = re.sub(r'[\$,]', '', number)
        clean_num = re.sub(r'\s*(million|billion|trillion|M|B|T)\s*', '', clean_num, flags=re.IGNORECASE)
        
        # Check for uncertainty qualifiers
        if any(word in number.lower() for word in ['about', 'approximately', 'around', 'roughly']):
            return self.specificity_weights['uncertain']
        
        # Check decimal places
        if '.' in clean_num:
            decimal_places = len(clean_num.split('.')[1].rstrip('%'))
            if decimal_places >= 2:
                return self.specificity_weights['two_plus_decimal']
            else:
                return self.specificity_weights['one_decimal']
        
        # Check if rounded large number
        if re.search(r'(million|billion|trillion|M|B|T)', number, re.IGNORECASE):
            # If it's a round number like "100 million"
            try:
                num_part = float(re.search(r'[\d.]+', clean_num).group())
                if num_part == int(num_part) and num_part % 10 == 0:
                    return self.specificity_weights['rounded']
            except:
                pass
        
        # Default to whole number
        return self.specificity_weights['whole']
    
    def _calculate_temporal_density(
        self,
        text: str,
        numerical_tokens: List[Tuple[str, str]]
    ) -> Tuple[float, float, int, int]:
        """
        Calculate forward-looking and backward-looking numerical density
        
        Returns:
            Tuple of (forward_density, backward_density, forward_count, backward_count)
        """
        # Get forward and backward looking statements
        forward_statements = identify_forward_looking_statements(text)
        backward_statements = identify_backward_looking_statements(text)
        
        # Count words in each
        forward_words = sum(len(tokenize_words(s, lowercase=False, remove_punct=True)) 
                           for s in forward_statements)
        backward_words = sum(len(tokenize_words(s, lowercase=False, remove_punct=True)) 
                            for s in backward_statements)
        
        # Count numerical tokens in each
        forward_count = sum(1 for _, context in numerical_tokens 
                           if any(context in stmt for stmt in forward_statements))
        backward_count = sum(1 for _, context in numerical_tokens 
                            if any(context in stmt for stmt in backward_statements))
        
        # Calculate densities
        forward_density = (forward_count / forward_words * 100) if forward_words > 0 else 0.0
        backward_density = (backward_count / backward_words * 100) if backward_words > 0 else 0.0
        
        return forward_density, backward_density, forward_count, backward_count
    
    def _calculate_contextualization(
        self,
        numerical_tokens: List[Tuple[str, str]]
    ) -> Tuple[float, int, int]:
        """
        Calculate contextualization quality score
        
        Returns:
            Tuple of (quality_score, well_contextualized_count, undercontextualized_count)
        """
        if not numerical_tokens:
            return 0.0, 0, 0
        
        context_scores = []
        well_contextualized = 0
        undercontextualized = 0
        
        for number, context in numerical_tokens:
            if self.use_llm and self.client:
                # Use LLM for assessment
                assessment = self.client.assess_contextualization(number, context)
                score = assessment.get('overall_score', 1.5)
                
                # Normalize to 0-3 scale
                if score >= 2.5:
                    well_contextualized += 1
                elif score <= 1.0:
                    undercontextualized += 1
                
                context_scores.append(score)
            else:
                # Use rule-based heuristic
                score = self._rule_based_contextualization(number, context)
                context_scores.append(score)
                
                if score >= 2.5:
                    well_contextualized += 1
                elif score <= 1.0:
                    undercontextualized += 1
        
        # Calculate average and normalize to 0-1 scale
        avg_score = sum(context_scores) / len(context_scores)
        quality_score = avg_score / 3.0
        
        return quality_score, well_contextualized, undercontextualized
    
    def _rule_based_contextualization(self, number: str, context: str) -> float:
        """
        Rule-based contextualization assessment (fallback)
        
        Returns:
            Score from 0-3
        """
        context_lower = context.lower()
        score = 0.0
        
        # Check for comparison words
        comparison_words = ['up from', 'down from', 'vs', 'versus', 'compared to', 
                          'year-over-year', 'yoy', 'qoq', 'quarter-over-quarter']
        if any(word in context_lower for word in comparison_words):
            score += 1.0
        
        # Check for explanation words
        explanation_words = ['driven by', 'due to', 'because', 'as a result', 
                           'reflecting', 'primarily', 'driven']
        if any(word in context_lower for word in explanation_words):
            score += 1.0
        
        # Check for implication words
        implication_words = ['positioning', 'enables', 'allows', 'supports', 
                           'demonstrates', 'indicates', 'shows']
        if any(word in context_lower for word in implication_words):
            score += 1.0
        
        return score
    
    def _benchmark_comparison(self, transparency_score: float) -> str:
        """Compare to S&P 500 benchmark"""
        benchmark = settings.SP500_NUMERIC_TRANSPARENCY
        
        if transparency_score > benchmark * 1.1:
            return "above"
        elif transparency_score < benchmark * 0.9:
            return "below"
        else:
            return "at"
    
    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, NumericalScores]:
        """Analyze numerical content for each section"""
        return {
            section_name: self.analyze(text)
            for section_name, text in sections.items()
            if text.strip()
        }
    
    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, NumericalScores]:
        """Analyze numerical content for each speaker"""
        return {
            speaker_name: self.analyze(text)
            for speaker_name, text in speakers.items()
            if text.strip()
        }
    
    def _empty_scores(self) -> NumericalScores:
        """Return empty scores for texts with no numbers"""
        return NumericalScores(
            numeric_transparency_score=0.0,
            numerical_specificity_index=0.0,
            forward_looking_density=0.0,
            backward_looking_density=0.0,
            forward_to_backward_ratio=0.0,
            contextualization_quality_score=0.0,
            total_numerical_tokens=0,
            forward_numerical_tokens=0,
            backward_numerical_tokens=0,
            well_contextualized_count=0,
            undercontextualized_count=0,
            vs_sp500_benchmark="below"
        )

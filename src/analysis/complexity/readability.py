"""
Language Complexity Analysis Module
Implements all 5 readability metrics as specified in PRD
"""
from dataclasses import dataclass
from typing import Dict
import math
from src.utils.text_utils import (
    tokenize_sentences,
    tokenize_words,
    count_syllables,
    count_complex_words,
    count_polysyllabic_words,
    calculate_word_character_ratio
)


@dataclass
class ComplexityScores:
    """Language complexity scores"""
    # Individual metrics
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog_index: float
    smog_index: float
    coleman_liau_index: float
    
    # Composite score
    composite_score: float
    complexity_level: str  # Very Simple, Simple, Moderate, Complex, Very Complex
    
    # Component counts for validation
    word_count: int
    sentence_count: int
    syllable_count: int
    complex_word_count: int


class ComplexityAnalyzer:
    """Analyzes language complexity using multiple readability formulas"""
    
    def __init__(self):
        """Initialize complexity analyzer"""
        self.complexity_levels = [
            (0, 20, "Very Simple"),
            (21, 40, "Simple"),
            (41, 60, "Moderate"),
            (61, 80, "Complex"),
            (81, 100, "Very Complex")
        ]
    
    def analyze(self, text: str) -> ComplexityScores:
        """
        Analyze language complexity
        
        Args:
            text: Text to analyze
            
        Returns:
            ComplexityScores object
        """
        # Tokenize
        sentences = tokenize_sentences(text)
        words = tokenize_words(text, lowercase=False, remove_punct=True)
        
        if not sentences or not words:
            return self._empty_scores()
        
        sentence_count = len(sentences)
        word_count = len(words)
        
        # Calculate syllable count
        syllable_count = sum(count_syllables(word) for word in words)
        
        # Calculate individual metrics
        fres = self._flesch_reading_ease(word_count, sentence_count, syllable_count)
        fkgl = self._flesch_kincaid_grade(word_count, sentence_count, syllable_count)
        fog = self._gunning_fog_index(text, words, sentences)
        smog = self._smog_index(text, sentences)
        cli = self._coleman_liau_index(text, words)
        
        # Calculate composite score
        composite = self._composite_score(fres, fkgl, fog, smog, cli)
        
        # Determine complexity level
        complexity_level = self._get_complexity_level(composite)
        
        return ComplexityScores(
            flesch_reading_ease=fres,
            flesch_kincaid_grade=fkgl,
            gunning_fog_index=fog,
            smog_index=smog,
            coleman_liau_index=cli,
            composite_score=composite,
            complexity_level=complexity_level,
            word_count=word_count,
            sentence_count=sentence_count,
            syllable_count=syllable_count,
            complex_word_count=count_complex_words(words)
        )
    
    def _flesch_reading_ease(self, word_count: int, sentence_count: int, syllable_count: int) -> float:
        """
        Calculate Flesch Reading Ease Score
        Formula: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        Range: 0-100 (higher = easier)
        """
        if word_count == 0 or sentence_count == 0:
            return 0.0
        
        words_per_sentence = word_count / sentence_count
        syllables_per_word = syllable_count / word_count
        
        score = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
        
        # Clamp to 0-100 range
        return max(0.0, min(100.0, score))
    
    def _flesch_kincaid_grade(self, word_count: int, sentence_count: int, syllable_count: int) -> float:
        """
        Calculate Flesch-Kincaid Grade Level
        Formula: 0.39(words/sentences) + 11.8(syllables/words) - 15.59
        """
        if word_count == 0 or sentence_count == 0:
            return 0.0
        
        words_per_sentence = word_count / sentence_count
        syllables_per_word = syllable_count / word_count
        
        grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
        
        return max(0.0, grade)
    
    def _gunning_fog_index(self, text: str, words: list, sentences: list) -> float:
        """
        Calculate Gunning Fog Index
        Formula: 0.4 × [(words/sentences) + 100(complex_words/words)]
        """
        if not words or not sentences:
            return 0.0
        
        word_count = len(words)
        sentence_count = len(sentences)
        complex_count = count_complex_words(words)
        
        words_per_sentence = word_count / sentence_count
        complex_ratio = (complex_count / word_count) * 100
        
        fog = 0.4 * (words_per_sentence + complex_ratio)
        
        return max(0.0, fog)
    
    def _smog_index(self, text: str, sentences: list) -> float:
        """
        Calculate SMOG Index
        Formula: √(polysyllabic_word_count) + 3
        """
        words = tokenize_words(text, lowercase=False, remove_punct=True)
        
        if not words:
            return 0.0
        
        polysyllabic_count = count_polysyllabic_words(words)
        
        smog = math.sqrt(polysyllabic_count) + 3
        
        return max(0.0, smog)
    
    def _coleman_liau_index(self, text: str, words: list) -> float:
        """
        Calculate Coleman-Liau Index
        Formula: 0.0588 × L - 0.296 × S - 15.8
        where L = letters per 100 words, S = sentences per 100 words
        """
        if not words:
            return 0.0
        
        l, s = calculate_word_character_ratio(text)
        
        cli = 0.0588 * l - 0.296 * s - 15.8
        
        return max(0.0, cli)
    
    def _composite_score(self, fres: float, fkgl: float, fog: float, smog: float, cli: float) -> float:
        """
        Calculate composite complexity score (0-100)
        All metrics normalized to same scale and averaged
        """
        # Normalize each metric to 0-100 scale
        # FRES is already 0-100 but needs inversion (lower = more complex)
        norm_fres = 100 - fres
        
        # Grade levels: normalize assuming range 0-20
        norm_fkgl = min(100, (fkgl / 20) * 100)
        norm_fog = min(100, (fog / 20) * 100)
        norm_smog = min(100, (smog / 20) * 100)
        norm_cli = min(100, (cli / 20) * 100)
        
        # Average all normalized scores
        composite = (norm_fres + norm_fkgl + norm_fog + norm_smog + norm_cli) / 5
        
        return round(composite, 2)
    
    def _get_complexity_level(self, composite_score: float) -> str:
        """Determine complexity level from composite score"""
        for min_score, max_score, level in self.complexity_levels:
            if min_score <= composite_score <= max_score:
                return level
        return "Unknown"
    
    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, ComplexityScores]:
        """
        Analyze complexity for each section
        
        Args:
            sections: Dict of section_name -> text
            
        Returns:
            Dict of section_name -> ComplexityScores
        """
        return {
            section_name: self.analyze(text)
            for section_name, text in sections.items()
            if text.strip()
        }
    
    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, ComplexityScores]:
        """
        Analyze complexity for each speaker
        
        Args:
            speakers: Dict of speaker_name -> text
            
        Returns:
            Dict of speaker_name -> ComplexityScores
        """
        return {
            speaker_name: self.analyze(text)
            for speaker_name, text in speakers.items()
            if text.strip()
        }
    
    def _empty_scores(self) -> ComplexityScores:
        """Return empty scores for invalid input"""
        return ComplexityScores(
            flesch_reading_ease=0.0,
            flesch_kincaid_grade=0.0,
            gunning_fog_index=0.0,
            smog_index=0.0,
            coleman_liau_index=0.0,
            composite_score=0.0,
            complexity_level="Unknown",
            word_count=0,
            sentence_count=0,
            syllable_count=0,
            complex_word_count=0
        )
    
    def get_interpretation(self, scores: ComplexityScores) -> Dict[str, str]:
        """
        Get human-readable interpretation of scores
        
        Args:
            scores: Complexity scores
            
        Returns:
            Dict with interpretations
        """
        interpretations = {}
        
        # FRES interpretation
        if scores.flesch_reading_ease >= 70:
            interpretations['fres'] = "Easy to read (7th-8th grade)"
        elif scores.flesch_reading_ease >= 60:
            interpretations['fres'] = "Standard difficulty (8th-9th grade)"
        elif scores.flesch_reading_ease >= 50:
            interpretations['fres'] = "Fairly difficult (10th-12th grade)"
        elif scores.flesch_reading_ease >= 30:
            interpretations['fres'] = "Difficult (college level)"
        else:
            interpretations['fres'] = "Very confusing (graduate level)"
        
        # FKGL interpretation
        grade = scores.flesch_kincaid_grade
        if grade <= 12:
            interpretations['fkgl'] = f"{int(grade)}th grade level"
        else:
            interpretations['fkgl'] = f"{int(grade - 12)} years of college"
        
        # Composite interpretation
        interpretations['composite'] = f"{scores.complexity_level} complexity"
        
        # Alert if too complex
        if scores.composite_score > 70:
            interpretations['alert'] = "⚠️ Potentially obfuscatory language"
        
        return interpretations

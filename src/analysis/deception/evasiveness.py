#!/usr/bin/env python3

"""
Evasiveness Scorer
Measures evasiveness in earnings call language
"""
from dataclasses import dataclass
from typing import List, Tuple
from src.utils.text_utils import tokenize_sentences, tokenize_words
from src.analysis.deception.linguistic_markers import LinguisticDeceptionMarkers
from config.settings import settings


@dataclass
class EvasivenessScores:
	"""Evasiveness metrics"""
	overall_evasiveness: float  # Composite score 0-100
	
	# Component metrics
	qualifier_density: float
	hedging_language_pct: float
	passive_voice_pct: float
	vague_pronoun_pct: float
	distancing_score: float
	
	# Comparisons
	vs_baseline: str  # "above", "at", "below"
	evasiveness_level: str  # "Low", "Moderate", "High", "Very High"
	
	# Examples
	most_evasive_sentences: List[Tuple[str, float]]
	
	
class EvasivenessAnalyzer:
	"""Measure evasiveness in language"""
	
	def __init__(self):
		self.linguistic_markers = LinguisticDeceptionMarkers()
		self.baseline = settings.SP500_EVASIVENESS_BASELINE  # 11.0
		
	def analyze(self, text: str) -> EvasivenessScores:
		"""
		Calculate evasiveness metrics
		
		Args:
			text: Input text
			
		Returns:
			EvasivenessScores object
		"""
		# Component calculations
		qualifier_density = self.linguistic_markers.calculate_qualifier_density(text)
		hedging_pct = self.linguistic_markers.calculate_hedging_density(text)
		passive_pct = self.linguistic_markers.detect_passive_voice(text)
		vague_pronoun_pct = self.linguistic_markers.calculate_vague_pronoun_usage(text)
		
		distancing_analysis = self.linguistic_markers.analyze_pronoun_distancing(text)
		distancing_score = distancing_analysis['distancing_score']
		
		# Composite evasiveness score
		overall = (
			qualifier_density * 0.25 +
			hedging_pct * 0.25 +
			passive_pct * 0.20 +
			vague_pronoun_pct * 0.15 +
			distancing_score * 0.15
		)
		
		# Compare to baseline
		vs_baseline = self._compare_to_baseline(overall)
		level = self._determine_level(overall)
		
		# Find most evasive sentences
		evasive_sentences = self._identify_evasive_sentences(text, top_n=5)
		
		return EvasivenessScores(
			overall_evasiveness=round(overall, 2),
			qualifier_density=round(qualifier_density, 2),
			hedging_language_pct=round(hedging_pct, 2),
			passive_voice_pct=round(passive_pct, 2),
			vague_pronoun_pct=round(vague_pronoun_pct, 2),
			distancing_score=round(distancing_score, 2),
			vs_baseline=vs_baseline,
			evasiveness_level=level,
			most_evasive_sentences=evasive_sentences
		)
	
	def _compare_to_baseline(self, score: float) -> str:
		"""Compare to S&P 500 baseline"""
		if score > self.baseline * 1.2:
			return "above"
		elif score < self.baseline * 0.8:
			return "below"
		else:
			return "at"
		
	def _determine_level(self, score: float) -> str:
		"""Determine evasiveness level"""
		if score >= self.baseline * 1.5:
			return "Very High"
		elif score >= self.baseline * 1.2:
			return "High"
		elif score >= self.baseline * 0.8:
			return "Moderate"
		else:
			return "Low"
		
	def _identify_evasive_sentences(
		self, 
		text: str, 
		top_n: int = 5
	) -> List[Tuple[str, float]]:
		"""
		Identify most evasive sentences
		
		Args:
			text: Input text
			top_n: Number of sentences to return
			
		Returns:
			List of (sentence, evasiveness_score) tuples
		"""
		sentences = tokenize_sentences(text)
		scored_sentences = []
		
		for sentence in sentences:
			if len(tokenize_words(sentence, lowercase=False)) < 5:
				continue  # Skip very short sentences
			
			score = self._score_sentence_evasiveness(sentence)
			scored_sentences.append((sentence, score))
			
		# Sort by score and return top N
		scored_sentences.sort(key=lambda x: x[1], reverse=True)
		return scored_sentences[:top_n]
	
	def _score_sentence_evasiveness(self, sentence: str) -> float:
		"""
		Score a single sentence for evasiveness
		
		Args:
			sentence: Sentence to score
			
		Returns:
			Evasiveness score (0-100)
		"""
		words = tokenize_words(sentence, lowercase=True, remove_punct=True)
		
		if not words:
			return 0.0
		
		# Check for evasiveness markers
		qualifiers = {'approximately', 'around', 'roughly', 'about', 'nearly', 'almost'}
		hedging = {'perhaps', 'possibly', 'maybe', 'might', 'could', 'somewhat'}
		vague = {'it', 'that', 'this', 'thing', 'things', 'stuff'}
		
		qualifier_count = sum(1 for w in words if w in qualifiers)
		hedging_count = sum(1 for w in words if w in hedging)
		vague_count = sum(1 for w in words if w in vague)
		
		# Calculate density
		total_evasive = qualifier_count + hedging_count + vague_count
		density = (total_evasive / len(words)) * 100
		
		# Check for passive voice
		passive_indicators = ['is', 'are', 'was', 'were', 'been', 'being']
		has_passive = any(word in words for word in passive_indicators)
		
		# Boost score if passive
		if has_passive:
			density *= 1.2
			
		return min(100, density * 5)  # Amplify for scoring
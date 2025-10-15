#!/usr/bin/env python3

"""
Linguistic Deception Markers
Detects linguistic patterns associated with deception and obfuscation
"""
from typing import Dict, List, Set
import re
from src.utils.text_utils import tokenize_words, tokenize_sentences
from config.settings import settings

# Try to import spaCy for advanced passive voice detection
try:
	import spacy
	SPACY_AVAILABLE = True
	try:
		nlp = spacy.load('en_core_web_sm')
	except OSError:
		SPACY_AVAILABLE = False
		nlp = None
except ImportError:
	SPACY_AVAILABLE = False
	nlp = None
	
	
class LinguisticDeceptionMarkers:
	"""Detects linguistic patterns associated with deception"""
	
	def __init__(self):
		"""Initialize with linguistic marker dictionaries"""
		self.hedging_words = {
			'perhaps', 'possibly', 'maybe', 'might', 'could',
			'somewhat', 'fairly', 'relatively', 'basically',
			'essentially', 'generally', 'largely', 'mostly',
			'probably', 'likely', 'arguably', 'presumably',
			'seemingly', 'apparently', 'allegedly', 'supposedly'
		}
		
		self.qualifiers = {
			'approximately', 'around', 'roughly', 'about',
			'nearly', 'almost', 'close to', 'in the range of',
			'ballpark', 'give or take', 'more or less',
			'somewhere', 'kind of', 'sort of', 'ish'
		}
		
		self.strong_modals = {
			'will', 'shall', 'must', 'definitely', 'certainly',
			'absolutely', 'clearly', 'obviously', 'undoubtedly',
			'unquestionably', 'surely', 'indeed'
		}
		
		self.weak_modals = {
			'might', 'could', 'may', 'possibly', 'perhaps',
			'maybe', 'potentially', 'would', 'should'
		}
		
		self.distancing_patterns = [
			r'\bthe company\b',
			r'\bthe organization\b',
			r'\bthe business\b',
			r'\bthe team\b',
			r'\bthe management\b'
		]
		
		self.inclusive_pronouns = {
			'we', 'us', 'our', 'ours', 'ourselves'
		}
		
	def calculate_hedging_density(self, text: str) -> float:
		"""
		Calculate percentage of hedging words
		
		Args:
			text: Input text
			
		Returns:
			Percentage of words that are hedging words (0-100)
		"""
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		
		if not words:
			return 0.0
		
		hedge_count = sum(1 for w in words if w in self.hedging_words)
		
		return (hedge_count / len(words)) * 100
	
	def calculate_qualifier_density(self, text: str) -> float:
		"""
		Calculate percentage of qualifier words and phrases
		
		Args:
			text: Input text
			
		Returns:
			Percentage of words that are qualifiers (0-100)
		"""
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		text_lower = text.lower()
		
		if not words:
			return 0.0
		
		# Count single-word qualifiers
		single_word_count = sum(1 for w in words if w in self.qualifiers)
		
		# Count multi-word qualifiers
		multi_word_count = sum(text_lower.count(phrase) for phrase in self.qualifiers if ' ' in phrase)
		
		total_qualifier_count = single_word_count + multi_word_count
		
		return (total_qualifier_count / len(words)) * 100
	
	def calculate_modal_weakness(
		self, 
		speakers: Dict[str, str],
		sentiment_scores = None
	) -> float:
		"""
		Calculate modal weakness score (weak modals vs strong modals)
		
		High ratio of weak to strong modals indicates uncertainty/hedging
		
		Args:
			speakers: Dict of speaker -> text
			sentiment_scores: Optional sentiment scores with modal counts
			
		Returns:
			Modal weakness score (0-100)
		"""
		# Combine all speaker text
		text = ' '.join(speakers.values()) if speakers else ''
		
		if not text:
			return 0.0
		
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		
		strong_count = sum(1 for w in words if w in self.strong_modals)
		weak_count = sum(1 for w in words if w in self.weak_modals)
		
		total_modals = strong_count + weak_count
		
		if total_modals == 0:
			return 50.0  # Neutral if no modals
		
		# Weakness score: higher = more weak modals
		weakness_ratio = weak_count / total_modals
		
		return weakness_ratio * 100
	
	def detect_passive_voice(self, text: str) -> float:
		"""
		Detect passive voice constructions
		
		Passive voice can indicate distancing/evasion
		
		Args:
			text: Input text
			
		Returns:
			Percentage of verb phrases in passive voice (0-100)
		"""
		if SPACY_AVAILABLE and nlp:
			return self._spacy_passive_detection(text)
		else:
			return self._simple_passive_detection(text)
		
	def _spacy_passive_detection(self, text: str) -> float:
		"""Use spaCy for accurate passive voice detection"""
		doc = nlp(text)
		
		passive_count = 0
		total_verbs = 0
		
		for token in doc:
			if token.pos_ == "VERB":
				total_verbs += 1
				
				# Check for passive voice indicators
				if token.dep_ == "auxpass":
					passive_count += 1
				elif "Pass" in token.morph.get("Voice", []):
					passive_count += 1
				# Check for passive pattern: be + past participle
				elif token.lemma_ == "be":
					# Look for past participle after 'be'
					for child in token.children:
						if child.tag_ == "VBN":  # Past participle
							passive_count += 1
							break
					
		return (passive_count / total_verbs * 100) if total_verbs > 0 else 0.0
	
	def _simple_passive_detection(self, text: str) -> float:
		"""Simple rule-based passive voice detection (fallback)"""
		sentences = tokenize_sentences(text)
		
		if not sentences:
			return 0.0
		
		passive_patterns = [
			r'\b(is|are|was|were|been|be)\s+\w+ed\b',
			r'\b(is|are|was|were|been|be)\s+being\s+\w+ed\b',
			r'\b(has|have|had)\s+been\s+\w+ed\b'
		]
		
		passive_count = 0
		
		for sentence in sentences:
			for pattern in passive_patterns:
				if re.search(pattern, sentence.lower()):
					passive_count += 1
					break  # Count each sentence only once
				
		return (passive_count / len(sentences)) * 100
	
	def analyze_pronoun_distancing(self, text: str) -> Dict[str, float]:
		"""
		Analyze pronoun usage patterns for distancing behavior
		
		Deception indicator: Using "the company" instead of "we/us/our"
		
		Args:
			text: Input text
			
		Returns:
			Dict with distancing metrics
		"""
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		text_lower = text.lower()
		
		# Count inclusive pronouns
		inclusive_count = sum(1 for w in words if w in self.inclusive_pronouns)
		
		# Count distancing phrases
		distancing_count = sum(
			len(re.findall(pattern, text_lower))
			for pattern in self.distancing_patterns
		)
		
		total = inclusive_count + distancing_count
		
		if total == 0:
			return {
				'distancing_ratio': 0.0,
				'inclusive_ratio': 0.0,
				'distancing_score': 0.0
			}
		
		distancing_ratio = distancing_count / total
		inclusive_ratio = inclusive_count / total
		
		return {
			'distancing_ratio': distancing_ratio,
			'inclusive_ratio': inclusive_ratio,
			'distancing_score': distancing_ratio * 100,  # 0-100 scale
			'inclusive_count': inclusive_count,
			'distancing_count': distancing_count
		}
	
	def calculate_vague_pronoun_usage(self, text: str) -> float:
		"""
		Calculate usage of vague pronouns (it, that, thing, etc.)
		
		High usage can indicate lack of specificity
		
		Args:
			text: Input text
			
		Returns:
			Percentage of vague pronouns (0-100)
		"""
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		
		if not words:
			return 0.0
		
		vague_pronouns = {'it', 'that', 'this', 'these', 'those', 'thing', 'things', 'stuff'}
		
		vague_count = sum(1 for w in words if w in vague_pronouns)
		
		return (vague_count / len(words)) * 100
	
	def detect_euphemisms(self, text: str) -> List[str]:
		"""
		Detect common business euphemisms that may obscure reality
		
		Args:
			text: Input text
			
		Returns:
			List of detected euphemisms
		"""
		euphemisms = {
			'challenged': 'struggling/failing',
			'rightsizing': 'layoffs',
			'negative growth': 'decline',
			'headwinds': 'problems',
			'strategic review': 'considering sale/closure',
			'streamlining': 'cutting',
			'rationalization': 'cuts',
			'optimization': 'cuts',
			'transition period': 'problems',
			'disappointed': 'failed',
			'evolving situation': 'crisis',
			'opportunities': 'problems'
		}
		
		text_lower = text.lower()
		found_euphemisms = []
		
		for euphemism, meaning in euphemisms.items():
			if euphemism in text_lower:
				found_euphemisms.append({
					'euphemism': euphemism,
					'likely_meaning': meaning,
					'occurrences': text_lower.count(euphemism)
				})
				
		return found_euphemisms
	
	def calculate_specificity_index(self, text: str) -> float:
		"""
		Calculate overall linguistic specificity
		
		High specificity = concrete, clear language
		Low specificity = vague, abstract language
		
		Args:
			text: Input text
			
		Returns:
			Specificity score (0-100, higher = more specific)
		"""
		# Inverse of hedging + qualifiers + vague pronouns
		hedging = self.calculate_hedging_density(text)
		qualifiers = self.calculate_qualifier_density(text)
		vague_pronouns = self.calculate_vague_pronoun_usage(text)
		
		# Combined vagueness
		vagueness = (hedging + qualifiers + vague_pronouns) / 3
		
		# Invert to get specificity
		specificity = 100 - vagueness
		
		return max(0, specificity)
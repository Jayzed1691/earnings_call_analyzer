#!/usr/bin/env python3

"""
Deception Risk Detector
Comprehensive analysis of potential deception indicators in earnings calls
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
from src.analysis.complexity.readability import ComplexityScores
from src.analysis.sentiment.hybrid_scorer import HybridSentimentScores
from src.analysis.numerical.transparency import NumericalScores
from src.core.transcript_processor import ProcessedTranscript
from src.analysis.deception.linguistic_markers import LinguisticDeceptionMarkers
from src.analysis.deception.evasiveness import EvasivenessAnalyzer
from src.utils.text_utils import tokenize_sentences, tokenize_words
from config.settings import settings


@dataclass
class DeceptionIndicators:
	"""Individual deception indicators (0-100 scale)"""
	# Linguistic indicators
	hedging_score: float
	qualifier_density: float
	modal_weakness_score: float
	passive_voice_ratio: float
	pronoun_distancing: float
	
	# Behavioral indicators
	complexity_spike_qa: float
	sentiment_drop_qa: float
	response_length_variance: float
	
	# Numerical indicators
	forward_avoidance: float
	vague_number_ratio: float
	contextualization_gap: float
	
	# Evasion indicators
	question_dodge_rate: float
	topic_deflection_score: float
	
	
@dataclass
class DeceptionRiskScore:
	"""Comprehensive deception risk assessment"""
	overall_risk_score: float  # 0-100
	risk_level: str  # Low, Moderate, High, Critical
	confidence: float  # 0-1
	
	indicators: DeceptionIndicators
	triggered_flags: List[str]
	risk_components: Dict[str, float]
	
	# Specific findings
	most_evasive_questions: List[Dict]
	complexity_hotspots: List[Tuple[str, float]]
	numerical_red_flags: List[Dict]
	
	
class DeceptionRiskAnalyzer:
	"""Detects potential deception or obfuscation in earnings calls"""
	
	def __init__(self):
		self.linguistic_analyzer = LinguisticDeceptionMarkers()
		self.evasiveness_analyzer = EvasivenessAnalyzer()
		
	def analyze(
		self,
		transcript: ProcessedTranscript,
		sentiment_scores: HybridSentimentScores,
		complexity_scores: ComplexityScores,
		numerical_scores: NumericalScores,
		section_analysis: Dict
	) -> DeceptionRiskScore:
		"""
		Comprehensive deception risk assessment
		
		Args:
			transcript: Processed transcript
			sentiment_scores: Overall sentiment analysis
			complexity_scores: Language complexity metrics
			numerical_scores: Numerical transparency metrics
			section_analysis: Section-level breakdowns
			
		Returns:
			DeceptionRiskScore with all indicators
		"""
		# Calculate individual indicators
		indicators = self._calculate_indicators(
			transcript, 
			sentiment_scores,
			complexity_scores, 
			numerical_scores, 
			section_analysis
		)
		
		# Calculate composite risk score
		risk_score, risk_components = self._calculate_risk_score(indicators)
		
		# Determine risk level
		risk_level = self._categorize_risk(risk_score)
		
		# Calculate confidence in assessment
		confidence = self._calculate_confidence(indicators, transcript)
		
		# Identify triggered flags
		flags = self._identify_flags(indicators, risk_score)
		
		# Find specific examples
		evasive_qa = self._identify_evasive_questions(transcript)
		complexity_hotspots = self._find_complexity_hotspots(transcript)
		numerical_flags = self._flag_numerical_issues(transcript, numerical_scores)
		
		return DeceptionRiskScore(
			overall_risk_score=risk_score,
			risk_level=risk_level,
			confidence=confidence,
			indicators=indicators,
			triggered_flags=flags,
			risk_components=risk_components,
			most_evasive_questions=evasive_qa,
			complexity_hotspots=complexity_hotspots,
			numerical_red_flags=numerical_flags
		)
	
	def _calculate_indicators(
		self,
		transcript: ProcessedTranscript,
		sentiment_scores: HybridSentimentScores,
		complexity_scores: ComplexityScores,
		numerical_scores: NumericalScores,
		section_analysis: Dict
	) -> DeceptionIndicators:
		"""Calculate all individual deception indicators"""
		
		text = transcript.cleaned_text
		
		# Linguistic indicators
		hedging_score = self.linguistic_analyzer.calculate_hedging_density(text)
		qualifier_density = self.linguistic_analyzer.calculate_qualifier_density(text)
		modal_weakness = self.linguistic_analyzer.calculate_modal_weakness(
			transcript.speakers, sentiment_scores.lexicon_scores
		)
		passive_ratio = self.linguistic_analyzer.detect_passive_voice(text)
		
		pronoun_analysis = self.linguistic_analyzer.analyze_pronoun_distancing(text)
		pronoun_distancing = pronoun_analysis.get('distancing_score', 0.0)
		
		# Behavioral indicators (section comparison)
		complexity_spike = self._calculate_complexity_spike(section_analysis)
		sentiment_drop = self._calculate_sentiment_drop(section_analysis)
		length_variance = self._calculate_response_variance(transcript)
		
		# Numerical indicators
		forward_avoidance = self._calculate_forward_avoidance(numerical_scores)
		vague_ratio = self._calculate_vague_number_ratio(numerical_scores)
		context_gap = (1 - numerical_scores.contextualization_quality_score) * 100
		
		# Evasion indicators
		if transcript.sections.get('qa'):
			dodge_rate = self._calculate_question_dodge_rate(transcript.sections['qa'])
			deflection = self._calculate_topic_deflection(transcript.sections['qa'])
		else:
			dodge_rate = 0.0
			deflection = 0.0
			
		return DeceptionIndicators(
			hedging_score=hedging_score,
			qualifier_density=qualifier_density,
			modal_weakness_score=modal_weakness,
			passive_voice_ratio=passive_ratio,
			pronoun_distancing=pronoun_distancing,
			complexity_spike_qa=complexity_spike,
			sentiment_drop_qa=sentiment_drop,
			response_length_variance=length_variance,
			forward_avoidance=forward_avoidance,
			vague_number_ratio=vague_ratio,
			contextualization_gap=context_gap,
			question_dodge_rate=dodge_rate,
			topic_deflection_score=deflection
		)
	
	def _calculate_complexity_spike(self, section_analysis: Dict) -> float:
		"""Calculate Q&A complexity spike vs prepared remarks"""
		prep = section_analysis.get('prepared_remarks')
		qa = section_analysis.get('qa')
		
		if not prep or not qa:
			return 0.0
		
		spike = qa.composite_score - prep.composite_score
		
		# Normalize to 0-100 scale (spike of 20+ is very suspicious)
		normalized = min(100, max(0, (spike / 20) * 100))
		return normalized
	
	def _calculate_sentiment_drop(self, section_analysis: Dict) -> float:
		"""Calculate sentiment drop from prepared remarks to Q&A"""
		# Section analysis should contain sentiment scores for each section
		# This is a simplified version - in practice, need section-specific sentiment
		# For now, return 0 as placeholder
		return 0.0
	
	def _calculate_response_variance(self, transcript: ProcessedTranscript) -> float:
		"""Calculate variance in response lengths (inconsistent = suspicious)"""
		qa_section = transcript.sections.get('qa', '')
		
		if not qa_section:
			return 0.0
		
		# Extract response lengths
		responses = self._extract_responses(qa_section)
		
		if len(responses) < 3:
			return 0.0
		
		lengths = [len(tokenize_words(r, lowercase=False)) for r in responses]
		
		# Calculate coefficient of variation (CV)
		mean_length = np.mean(lengths)
		std_length = np.std(lengths)
		
		if mean_length == 0:
			return 0.0
		
		cv = (std_length / mean_length) * 100
		
		# High variance (CV > 100) is suspicious
		return min(100, cv)
	
	def _extract_responses(self, qa_text: str) -> List[str]:
		"""Extract management responses from Q&A text"""
		# Simple heuristic: Look for speaker patterns
		# In production, use the transcript processor's speaker identification
		responses = []
		
		# Split by common patterns
		parts = qa_text.split('\n\n')
		
		for part in parts:
			# If it's a management response (not analyst question)
			if any(title in part for title in ['CEO', 'CFO', 'Officer', 'Director']):
				# Extract the actual response text
				lines = part.split('\n')
				if len(lines) > 1:
					response_text = '\n'.join(lines[1:])
					responses.append(response_text)
					
		return responses
	
	def _calculate_forward_avoidance(self, numerical_scores: NumericalScores) -> float:
		"""Calculate forward-looking numerical avoidance score"""
		ratio = numerical_scores.forward_to_backward_ratio
		
		# Ratio < 0.5 is concerning, < 0.3 is very concerning
		if ratio >= 0.7:
			return 0.0
		elif ratio >= 0.5:
			return 30.0
		elif ratio >= 0.3:
			return 60.0
		else:
			return 90.0
		
	def _calculate_vague_number_ratio(self, numerical_scores: NumericalScores) -> float:
		"""Calculate ratio of vague/rounded numbers"""
		# Use specificity index as inverse measure
		specificity = numerical_scores.numerical_specificity_index
		
		# Specificity ranges 0.3-2.0, where 0.3 is vague, 2.0 is precise
		# Invert to get vagueness score
		vagueness = 1.0 - ((specificity - 0.3) / 1.7)
		
		return max(0, min(100, vagueness * 100))
	
	def _calculate_question_dodge_rate(self, qa_text: str) -> float:
		"""Calculate percentage of questions that were dodged"""
		# This is a simplified heuristic
		# In production, use the QuestionEvasionDetector
		
		sentences = tokenize_sentences(qa_text)
		
		# Look for deflection phrases
		deflection_phrases = [
			"let me talk about",
			"what i would say is",
			"more broadly",
			"stepping back",
			"in general",
			"i think the important thing",
			"what's really important"
		]
		
		deflection_count = 0
		for sentence in sentences:
			sentence_lower = sentence.lower()
			if any(phrase in sentence_lower for phrase in deflection_phrases):
				deflection_count += 1
				
		# Rough heuristic: if 20%+ of sentences have deflection phrases
		if len(sentences) == 0:
			return 0.0
		
		deflection_rate = (deflection_count / len(sentences)) * 100
		return min(100, deflection_rate * 5)  # Amplify for scoring
	
	def _calculate_topic_deflection(self, qa_text: str) -> float:
		"""Calculate topic deflection score"""
		# Simplified version - full implementation would use NLP topic modeling
		
		# Look for topic change indicators
		topic_change_phrases = [
			"but what i really want to emphasize",
			"more importantly",
			"what we should focus on",
			"the real story here",
			"let me pivot to"
		]
		
		sentences = tokenize_sentences(qa_text)
		
		change_count = sum(
			1 for s in sentences 
			if any(phrase in s.lower() for phrase in topic_change_phrases)
		)
		
		if len(sentences) == 0:
			return 0.0
		
		return min(100, (change_count / len(sentences)) * 500)
	
	def _calculate_risk_score(
		self, 
		indicators: DeceptionIndicators
	) -> Tuple[float, Dict[str, float]]:
		"""
		Calculate composite risk score from indicators
		
		Weighted combination:
		- Linguistic: 25%
		- Behavioral: 25%
		- Numerical: 30%
		- Evasion: 20%
		"""
		components = {
			'linguistic': (
				indicators.hedging_score * 0.25 +
				indicators.qualifier_density * 0.25 +
				indicators.modal_weakness_score * 0.20 +
				indicators.passive_voice_ratio * 0.15 +
				indicators.pronoun_distancing * 0.15
			),
			'behavioral': (
				indicators.complexity_spike_qa * 0.45 +
				indicators.sentiment_drop_qa * 0.35 +
				indicators.response_length_variance * 0.20
			),
			'numerical': (
				indicators.forward_avoidance * 0.35 +
				indicators.vague_number_ratio * 0.30 +
				indicators.contextualization_gap * 0.35
			),
			'evasion': (
				indicators.question_dodge_rate * 0.60 +
				indicators.topic_deflection_score * 0.40
			)
		}
		
		overall = (
			components['linguistic'] * 0.25 +
			components['behavioral'] * 0.25 +
			components['numerical'] * 0.30 +
			components['evasion'] * 0.20
		)
		
		return round(overall, 2), components
	
	def _categorize_risk(self, risk_score: float) -> str:
		"""Map risk score to category"""
		if risk_score >= settings.DECEPTION_RISK_CRITICAL:  # 70
			return "Critical"
		elif risk_score >= settings.DECEPTION_RISK_WARNING:  # 50
			return "High"
		elif risk_score >= 30:
			return "Moderate"
		else:
			return "Low"
	
	def _calculate_confidence(
		self, 
		indicators: DeceptionIndicators,
		transcript: ProcessedTranscript
	) -> float:
		"""Calculate confidence in deception assessment"""
		
		# Confidence based on:
		# 1. Transcript completeness (has Q&A?)
		# 2. Number of speakers identified
		# 3. Text length
		
		confidence_factors = []
		
		# Q&A section present
		if transcript.sections.get('qa'):
			confidence_factors.append(1.0)
		else:
			confidence_factors.append(0.5)
			
		# Sufficient length
		if transcript.word_count >= 2000:
			confidence_factors.append(1.0)
		elif transcript.word_count >= 1000:
			confidence_factors.append(0.8)
		else:
			confidence_factors.append(0.6)
			
		# Multiple speakers
		if len(transcript.speakers) >= 3:
			confidence_factors.append(1.0)
		elif len(transcript.speakers) >= 2:
			confidence_factors.append(0.8)
		else:
			confidence_factors.append(0.6)
			
		return round(np.mean(confidence_factors), 2)
	
	def _identify_flags(
		self, 
		indicators: DeceptionIndicators, 
		risk_score: float
	) -> List[str]:
		"""Identify triggered red flags"""
		flags = []
		
		# Linguistic flags
		if indicators.hedging_score > 15:
			flags.append(f"High hedging language ({indicators.hedging_score:.1f}%)")
			
		if indicators.qualifier_density > 10:
			flags.append(f"Excessive qualifiers ({indicators.qualifier_density:.1f}%)")
			
		if indicators.passive_voice_ratio > 30:
			flags.append(f"High passive voice usage ({indicators.passive_voice_ratio:.1f}%)")
			
		if indicators.pronoun_distancing > 40:
			flags.append(f"Pronoun distancing detected ({indicators.pronoun_distancing:.1f}%)")
			
		# Behavioral flags
		if indicators.complexity_spike_qa > 60:
			flags.append("Significant complexity spike in Q&A")
			
		if indicators.sentiment_drop_qa > 50:
			flags.append("Major sentiment drop during Q&A")
			
		if indicators.response_length_variance > 80:
			flags.append("Highly inconsistent response lengths")
			
		# Numerical flags
		if indicators.forward_avoidance > 70:
			flags.append("Avoidance of forward-looking numbers")
			
		if indicators.vague_number_ratio > 60:
			flags.append("Excessive use of vague/rounded numbers")
			
		if indicators.contextualization_gap > 60:
			flags.append("Poor numerical contextualization")
			
		# Evasion flags
		if indicators.question_dodge_rate > 50:
			flags.append(f"High question evasion rate ({indicators.question_dodge_rate:.1f}%)")
			
		if indicators.topic_deflection_score > 50:
			flags.append("Frequent topic deflection")
			
		# Overall risk flag
		if risk_score >= settings.DECEPTION_RISK_CRITICAL:
			flags.append(f"⚠️ CRITICAL DECEPTION RISK ({risk_score:.0f}/100)")
		elif risk_score >= settings.DECEPTION_RISK_WARNING:
			flags.append(f"⚠️ HIGH DECEPTION RISK ({risk_score:.0f}/100)")
			
		return flags
	
	def _identify_evasive_questions(
		self, 
		transcript: ProcessedTranscript
	) -> List[Dict]:
		"""Identify most evasive Q&A exchanges"""
		qa_text = transcript.sections.get('qa', '')
		
		if not qa_text:
			return []
		
		# This is simplified - full implementation in question_evasion.py
		evasive_exchanges = []
		
		# Look for patterns indicating evasion
		evasion_markers = [
			("non-answer", ["let me talk about", "what's important is"]),
			("deflection", ["more broadly", "stepping back"]),
			("vagueness", ["approximately", "around", "roughly"])
		]
		
		# Find exchanges with these markers
		for marker_type, phrases in evasion_markers:
			for phrase in phrases:
				if phrase in qa_text.lower():
					# Extract context around the phrase
					idx = qa_text.lower().find(phrase)
					context_start = max(0, idx - 200)
					context_end = min(len(qa_text), idx + 200)
					context = qa_text[context_start:context_end]
					
					evasive_exchanges.append({
						'type': marker_type,
						'marker': phrase,
						'context': context.strip(),
						'evasiveness_score': 0.7
					})
					
		# Return top 5 most evasive
		return sorted(evasive_exchanges, key=lambda x: x['evasiveness_score'], reverse=True)[:5]
	
	def _find_complexity_hotspots(
		self, 
		transcript: ProcessedTranscript
	) -> List[Tuple[str, float]]:
		"""Find sentences/passages with unusually high complexity"""
		from src.analysis.complexity.readability import ComplexityAnalyzer
		
		analyzer = ComplexityAnalyzer()
		sentences = tokenize_sentences(transcript.cleaned_text)
		
		hotspots = []
		
		for sentence in sentences:
			if len(tokenize_words(sentence, lowercase=False)) < 10:
				continue  # Skip short sentences
			
			scores = analyzer.analyze(sentence)
			
			if scores.composite_score > 75:  # Very complex
				hotspots.append((sentence, scores.composite_score))
			
		# Return top 5 most complex
		hotspots.sort(key=lambda x: x[1], reverse=True)
		return hotspots[:5]
	
	def _flag_numerical_issues(
		self, 
		transcript: ProcessedTranscript,
		numerical_scores: NumericalScores
	) -> List[Dict]:
		"""Flag specific numerical transparency issues"""
		flags = []
		
		# Low contextualization
		if numerical_scores.contextualization_quality_score < 0.5:
			flags.append({
				'issue': 'Low contextualization quality',
				'score': numerical_scores.contextualization_quality_score,
				'description': f"Only {numerical_scores.well_contextualized_count} of {numerical_scores.total_numerical_tokens} numbers are well-contextualized",
				'severity': 'high'
			})
			
		# Forward avoidance
		if numerical_scores.forward_to_backward_ratio < 0.5:
			flags.append({
				'issue': 'Forward-looking number avoidance',
				'score': numerical_scores.forward_to_backward_ratio,
				'description': f"Forward-looking density ({numerical_scores.forward_looking_density:.1f}%) much lower than backward ({numerical_scores.backward_looking_density:.1f}%)",
				'severity': 'high'
			})
			
		# Low specificity
		if numerical_scores.numerical_specificity_index < 0.8:
			flags.append({
				'issue': 'Low numerical specificity',
				'score': numerical_scores.numerical_specificity_index,
				'description': "Heavy use of rounded/vague numbers",
				'severity': 'moderate'
			})
			
		# Below benchmark
		if numerical_scores.vs_sp500_benchmark == "below":
			flags.append({
				'issue': 'Below S&P 500 benchmark',
				'score': numerical_scores.numeric_transparency_score,
				'description': f"{numerical_scores.numeric_transparency_score:.2f}% vs {settings.SP500_NUMERIC_TRANSPARENCY}% benchmark",
				'severity': 'moderate'
			})
			
		return flags
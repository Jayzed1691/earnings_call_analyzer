#!/usr/bin/env python3

"""
Question Evasion Detector
Analyzes analyst questions vs management responses to detect evasion
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re
import json
from src.utils.text_utils import tokenize_sentences, tokenize_words
from src.models.ollama_client import ollama_client
from config.settings import settings

# Try to use spaCy for better topic extraction
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
	
	
@dataclass
class QuestionResponse:
	"""Represents a Q&A pair"""
	question: str
	response: str
	analyst: str
	responder: str
	
	# Analysis
	response_relevance: float  # 0-1
	is_evasive: bool
	evasion_type: str  # "direct", "deflection", "vague", "non-answer", "topic_change"
	key_question_topics: List[str]
	response_topics: List[str]
	topic_overlap: float  # 0-1
	
	
class QuestionEvasionDetector:
	"""Detects when management evades analyst questions"""
	
	def __init__(self):
		self.use_llm = True  # Can be configured
		
	def analyze_qa_section(self, qa_text: str) -> List[QuestionResponse]:
		"""
		Parse and analyze all Q&A pairs
		
		Args:
			qa_text: Q&A section text
			
		Returns:
			List of analyzed QuestionResponse objects
		"""
		qa_pairs = self._extract_qa_pairs(qa_text)
		analyzed_pairs = []
		
		for question, response, analyst, responder in qa_pairs:
			analysis = self._analyze_pair(question, response)
			
			analyzed_pairs.append(QuestionResponse(
				question=question,
				response=response,
				analyst=analyst,
				responder=responder,
				response_relevance=analysis['relevance'],
				is_evasive=analysis['is_evasive'],
				evasion_type=analysis['evasion_type'],
				key_question_topics=analysis['question_topics'],
				response_topics=analysis['response_topics'],
				topic_overlap=analysis['topic_overlap']
			))
			
		return analyzed_pairs
	
	def _extract_qa_pairs(self, qa_text: str) -> List[Tuple[str, str, str, str]]:
		"""
		Extract Q&A pairs from text
		
		Returns:
			List of (question, response, analyst, responder) tuples
		"""
		pairs = []
		
		# Pattern to match Q&A exchanges
		# Look for "Analyst Name - Firm:" followed by text, then "Executive - Title:" followed by text
		
		# Split into paragraphs
		paragraphs = qa_text.split('\n\n')
		
		i = 0
		while i < len(paragraphs):
			para = paragraphs[i]
			
			# Check if this is a question (contains "Analyst" or ends with "?")
			is_question = 'analyst' in para.lower() or para.strip().endswith('?')
			
			if is_question and i + 1 < len(paragraphs):
				# Extract question
				question_lines = para.split('\n')
				if len(question_lines) > 1:
					analyst = question_lines[0].strip()
					question = '\n'.join(question_lines[1:]).strip()
				else:
					analyst = "Unknown Analyst"
					question = para.strip()
					
				# Extract response (next paragraph)
				response_para = paragraphs[i + 1]
				response_lines = response_para.split('\n')
				
				if len(response_lines) > 1:
					responder = response_lines[0].strip()
					response = '\n'.join(response_lines[1:]).strip()
				else:
					responder = "Unknown Executive"
					response = response_para.strip()
					
				pairs.append((question, response, analyst, responder))
				i += 2  # Skip the response paragraph
			else:
				i += 1
				
		return pairs
	
	def _analyze_pair(self, question: str, response: str) -> Dict:
		"""
		Analyze a single Q&A pair for evasion
		
		Args:
			question: Analyst question
			response: Management response
			
		Returns:
			Dict with analysis results
		"""
		# Extract topics
		question_topics = self._extract_topics(question)
		response_topics = self._extract_topics(response)
		
		# Calculate topic overlap
		overlap = self._calculate_topic_overlap(question_topics, response_topics)
		
		# Check for evasion patterns (rule-based)
		evasion_signals = {
			'deflection': self._check_deflection(response),
			'vague': self._check_vagueness(response),
			'topic_change': overlap < 0.3,
			'length_mismatch': self._check_length_mismatch(question, response)
		}
		
		# Determine if evasive
		is_evasive = any([
			evasion_signals['deflection'],
			evasion_signals['vague'],
			evasion_signals['topic_change']
		])
		
		# Determine evasion type
		if not is_evasive:
			evasion_type = "direct"
		else:
			evasion_type = max(evasion_signals, key=evasion_signals.get)
			
		# Use LLM for relevance scoring if available
		if self.use_llm:
			relevance = self._llm_relevance_score(question, response)
		else:
			# Fallback: use topic overlap as proxy
			relevance = overlap
			
		return {
			'relevance': relevance,
			'is_evasive': is_evasive,
			'evasion_type': evasion_type,
			'question_topics': question_topics,
			'response_topics': response_topics,
			'topic_overlap': overlap
		}
	
	def _extract_topics(self, text: str) -> List[str]:
		"""
		Extract key topics/entities from text
		
		Args:
			text: Input text
			
		Returns:
			List of topic keywords
		"""
		if SPACY_AVAILABLE and nlp:
			return self._spacy_topic_extraction(text)
		else:
			return self._simple_topic_extraction(text)
		
	def _spacy_topic_extraction(self, text: str) -> List[str]:
		"""Use spaCy for topic extraction"""
		doc = nlp(text)
		
		topics = []
		
		# Extract named entities
		for ent in doc.ents:
			topics.append(ent.text.lower())
			
		# Extract noun chunks
		for chunk in doc.noun_chunks:
			# Filter out very common words
			if chunk.root.text.lower() not in {'it', 'this', 'that', 'thing', 'we', 'you'}:
				topics.append(chunk.text.lower())
				
		# Remove duplicates while preserving order
		seen = set()
		unique_topics = []
		for topic in topics:
			if topic not in seen:
				seen.add(topic)
				unique_topics.append(topic)
				
		return unique_topics
	
	def _simple_topic_extraction(self, text: str) -> List[str]:
		"""Simple keyword-based topic extraction (fallback)"""
		words = tokenize_words(text, lowercase=True, remove_punct=True)
		
		# Filter stopwords and short words
		stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
					'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
					'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
					'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
					'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
					'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
		
		topics = [
			word for word in words 
			if word not in stopwords and len(word) > 3
		]
		
		# Return unique topics
		return list(dict.fromkeys(topics))  # Preserves order
	
	def _calculate_topic_overlap(
		self, 
		question_topics: List[str], 
		response_topics: List[str]
	) -> float:
		"""
		Calculate overlap between question and response topics
		
		Args:
			question_topics: Topics from question
			response_topics: Topics from response
			
		Returns:
			Overlap score (0-1)
		"""
		if not question_topics or not response_topics:
			return 0.0
		
		# Convert to sets for intersection
		q_set = set(question_topics)
		r_set = set(response_topics)
		
		# Calculate Jaccard similarity
		intersection = len(q_set & r_set)
		union = len(q_set | r_set)
		
		if union == 0:
			return 0.0
		
		return intersection / union
	
	def _check_deflection(self, response: str) -> bool:
		"""Check if response shows deflection patterns"""
		deflection_phrases = [
			"let me talk about",
			"what i would say is",
			"more broadly",
			"stepping back",
			"in general",
			"i think the important thing",
			"what's really important",
			"the real story here",
			"what we should focus on",
			"let me pivot to"
		]
		
		response_lower = response.lower()
		return any(phrase in response_lower for phrase in deflection_phrases)
	
	def _check_vagueness(self, response: str) -> bool:
		"""Check if response is excessively vague"""
		words = tokenize_words(response, lowercase=True, remove_punct=True)
		
		if not words:
			return False
		
		vague_words = {
			'approximately', 'around', 'roughly', 'about',
			'generally', 'typically', 'usually', 'often',
			'possibly', 'probably', 'maybe', 'perhaps',
			'kind of', 'sort of', 'somewhat'
		}
		
		vague_count = sum(1 for w in words if w in vague_words)
		vague_density = vague_count / len(words)
		
		# If > 5% of words are vague qualifiers, flag as vague
		return vague_density > 0.05
	
	def _check_length_mismatch(self, question: str, response: str) -> bool:
		"""Check if response is suspiciously short relative to question complexity"""
		q_words = len(tokenize_words(question, lowercase=False))
		r_words = len(tokenize_words(response, lowercase=False))
		
		# If response is less than half the question length, might be evasive
		# (unless question is very long)
		if q_words > 30 and r_words < q_words * 0.5:
			return True
		
		# Or if response is extremely short (< 20 words)
		if r_words < 20:
			return True
		
		return False
	
	def _llm_relevance_score(self, question: str, response: str) -> float:
		"""
		Use LLM to score how well response addresses question
		
		Args:
			question: Analyst question
			response: Management response
			
		Returns:
			Relevance score (0-1)
		"""
		system_prompt = """You are an expert analyst evaluating earnings call Q&A sessions.
Your task is to determine how well a management response addresses an analyst's question."""
		
		user_prompt = f"""Rate how well this response addresses the analyst's question.

Question: "{question}"

Response: "{response}"

Evaluate:
1. Does the response directly address the core question?
2. Are specific details provided?
3. Is there deflection or topic changing?

Score from 0.0 (completely evasive/non-responsive) to 1.0 (directly and thoroughly addresses all aspects).

Respond ONLY with valid JSON in this exact format:
{{
	"relevance_score": 0.75,
	"addresses_question": true,
	"reasoning": "Response provides specific details but deflects slightly"
}}"""
		
		try:
			result = ollama_client.generate(
				model=settings.SENTIMENT_MODEL,
				prompt=user_prompt,
				system_prompt=system_prompt,
				json_mode=True,
				temperature=0.1
			)
			
			parsed = json.loads(result)
			return parsed.get('relevance_score', 0.5)
		
		except Exception as e:
			print(f"Warning: LLM relevance scoring failed: {e}")
			# Fallback to topic overlap
			question_topics = self._extract_topics(question)
			response_topics = self._extract_topics(response)
			return self._calculate_topic_overlap(question_topics, response_topics)
		
	def calculate_overall_evasion_rate(
		self, 
		analyzed_pairs: List[QuestionResponse]
	) -> float:
		"""
		Calculate overall question evasion rate
		
		Args:
			analyzed_pairs: List of analyzed Q&A pairs
			
		Returns:
			Evasion rate (0-100)
		"""
		if not analyzed_pairs:
			return 0.0
		
		evasive_count = sum(1 for pair in analyzed_pairs if pair.is_evasive)
		
		return (evasive_count / len(analyzed_pairs)) * 100
	
	def get_most_evasive_questions(
		self,
		analyzed_pairs: List[QuestionResponse],
		top_n: int = 5
	) -> List[QuestionResponse]:
		"""
		Get the most evasive Q&A exchanges
		
		Args:
			analyzed_pairs: List of analyzed pairs
			top_n: Number to return
			
		Returns:
			List of most evasive exchanges
		"""
		# Sort by relevance score (lower = more evasive)
		sorted_pairs = sorted(analyzed_pairs, key=lambda x: x.response_relevance)
		
		return sorted_pairs[:top_n]
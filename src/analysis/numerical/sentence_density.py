"""
Sentence-Level Numeric Density Analysis Module

Analyzes numeric content density at the sentence level to identify:
- Proportion of numerically dense sentences per transcript
- Distribution patterns (where numerics cluster)
- Informativeness metrics based on numeric content
"""
from dataclasses import dataclass
from typing import List, Tuple, Dict
import numpy as np
from src.utils.text_utils import tokenize_sentences, tokenize_words, extract_numerical_tokens


@dataclass
class SentenceDensityMetrics:
	"""Sentence-level numeric density analysis metrics"""
	# Sentence classification by density
	total_sentences: int
	numeric_dense_sentences: int  # >10% of words are numbers
	numeric_moderate_sentences: int  # 5-10% numbers
	numeric_sparse_sentences: int  # 1-5% numbers
	narrative_sentences: int  # 0% numbers (pure narrative)

	# Density statistics
	mean_numeric_density: float  # Average % across all sentences
	median_numeric_density: float
	std_numeric_density: float  # Variance in density (consistency measure)
	max_numeric_density: float  # Most dense sentence
	min_numeric_density: float  # Least dense sentence

	# Distribution percentiles
	p25_density: float  # 25th percentile
	p75_density: float  # 75th percentile

	# Proportion metrics (key metrics for research)
	proportion_numeric_dense: float  # % of sentences that are dense
	proportion_narrative: float  # % of sentences with no numbers

	# Top dense sentences (for inspection)
	top_dense_sentences: List[Tuple[str, float]]  # (sentence, density %)

	# Density by sentence position
	density_by_position: List[float]  # Density for each sentence in order


@dataclass
class DistributionPattern:
	"""Numeric density distribution patterns within transcript"""
	# Positional analysis (beginning/middle/end)
	beginning_density: float  # First 20% of sentences
	middle_density: float  # Middle 60% of sentences
	end_density: float  # Last 20% of sentences

	# Pattern classification
	pattern_type: str  # "front-loaded", "back-loaded", "uniform", "clustered", "scattered"
	pattern_confidence: float  # 0-1 confidence in pattern classification

	# Clustering metrics
	cluster_count: int  # Number of high-density clusters (rolling window)
	cluster_positions: List[Tuple[int, int]]  # [(start_idx, end_idx), ...]
	cluster_densities: List[float]  # Average density of each cluster

	# Q&A specific patterns (if applicable)
	question_avg_density: float  # Average density in questions
	answer_avg_density: float  # Average density in answers
	qa_density_differential: float  # Answer - Question density

	# Speaker patterns (if speaker info available)
	speaker_densities: Dict[str, float]  # speaker_role -> avg_density

	# Variance analysis
	density_variance_ratio: float  # std/mean, measures consistency
	coefficient_of_variation: float  # Normalized variance


@dataclass
class InformativenessMetrics:
	"""Metrics relating numeric content to informativeness and forecast relevance"""
	# Core metric - Numeric Inclusion Ratio
	numeric_inclusion_ratio: float  # 0-1, % of all sentences that contain numbers

	# Component metrics
	guidance_numeric_density: float  # Forward-looking numeric content
	results_numeric_density: float  # Backward-looking numeric content
	specificity_weighted_nir: float  # NIR weighted by number precision

	# Informativeness indicators (0-100 scales)
	informativeness_score: float  # Composite score
	forecast_relevance_score: float  # Emphasis on forward-looking numerics

	# Strategic insight signals
	quantitative_disclosure_level: str  # "very_high", "high", "medium", "low", "very_low"
	transparency_tier: str  # "top_quartile", "above_average", "average", "below_average", "bottom_quartile"

	# Risk assessment integration
	numeric_avoidance_risk: float  # 0-100, low numeric content = higher risk
	vagueness_penalty: float  # 0-100, penalty for imprecise numbers

	# Contextual quality
	contextualization_score: float  # 0-1, how well numbers are explained

	# Benchmark comparison
	vs_sp500_informativeness: str  # "above", "at", "below"


class SentenceLevelDensityAnalyzer:
	"""Analyzes numeric density at sentence level and identifies patterns"""

	# Density thresholds for classification
	DENSE_THRESHOLD = 10.0  # % of words that are numbers
	MODERATE_THRESHOLD = 5.0
	SPARSE_THRESHOLD = 1.0

	# Pattern detection thresholds
	CLUSTER_WINDOW_SIZE = 5  # sentences
	CLUSTER_DENSITY_THRESHOLD = 12.0  # % to be considered cluster

	def __init__(self):
		"""Initialize sentence-level density analyzer"""
		pass

	def analyze_sentence_density(self, text: str) -> SentenceDensityMetrics:
		"""
		Analyze numeric density at sentence level

		Args:
			text: Text to analyze

		Returns:
			SentenceDensityMetrics with detailed sentence-level analysis
		"""
		sentences = tokenize_sentences(text)

		if not sentences:
			return self._empty_sentence_metrics()

		# Calculate density for each sentence
		densities = []
		sentence_classifications = {
			'dense': 0,
			'moderate': 0,
			'sparse': 0,
			'narrative': 0
		}

		for sentence in sentences:
			density = self._calculate_sentence_density(sentence)
			densities.append((sentence, density))

			# Classify sentence
			if density >= self.DENSE_THRESHOLD:
				sentence_classifications['dense'] += 1
			elif density >= self.MODERATE_THRESHOLD:
				sentence_classifications['moderate'] += 1
			elif density >= self.SPARSE_THRESHOLD:
				sentence_classifications['sparse'] += 1
			else:
				sentence_classifications['narrative'] += 1

		# Extract density values for statistics
		density_values = [d for _, d in densities]

		# Calculate statistics
		mean_density = np.mean(density_values)
		median_density = np.median(density_values)
		std_density = np.std(density_values)
		max_density = np.max(density_values)
		min_density = np.min(density_values)
		p25 = np.percentile(density_values, 25)
		p75 = np.percentile(density_values, 75)

		# Proportion metrics
		total = len(sentences)
		prop_dense = sentence_classifications['dense'] / total
		prop_narrative = sentence_classifications['narrative'] / total

		# Top dense sentences
		top_dense = sorted(densities, key=lambda x: x[1], reverse=True)[:10]

		return SentenceDensityMetrics(
			total_sentences=total,
			numeric_dense_sentences=sentence_classifications['dense'],
			numeric_moderate_sentences=sentence_classifications['moderate'],
			numeric_sparse_sentences=sentence_classifications['sparse'],
			narrative_sentences=sentence_classifications['narrative'],
			mean_numeric_density=mean_density,
			median_numeric_density=median_density,
			std_numeric_density=std_density,
			max_numeric_density=max_density,
			min_numeric_density=min_density,
			p25_density=p25,
			p75_density=p75,
			proportion_numeric_dense=prop_dense,
			proportion_narrative=prop_narrative,
			top_dense_sentences=top_dense,
			density_by_position=density_values
		)

	def analyze_distribution_patterns(
		self,
		sentence_metrics: SentenceDensityMetrics,
		sections: Dict[str, str] = None,
		speakers: Dict[str, str] = None
	) -> DistributionPattern:
		"""
		Analyze distribution patterns of numeric density

		Args:
			sentence_metrics: Output from analyze_sentence_density
			sections: Optional dict of section_name -> text
			speakers: Optional dict of speaker_name -> text

		Returns:
			DistributionPattern analysis
		"""
		densities = sentence_metrics.density_by_position
		total = len(densities)

		# Positional analysis (beginning/middle/end)
		beginning_idx = int(total * 0.2)
		end_idx = int(total * 0.8)

		beginning_density = np.mean(densities[:beginning_idx]) if beginning_idx > 0 else 0.0
		middle_density = np.mean(densities[beginning_idx:end_idx]) if end_idx > beginning_idx else 0.0
		end_density = np.mean(densities[end_idx:]) if total > end_idx else 0.0

		# Classify pattern type
		pattern_type, pattern_confidence = self._classify_pattern(
			beginning_density, middle_density, end_density, densities
		)

		# Identify clusters using rolling window
		clusters, cluster_densities = self._identify_clusters(densities)

		# Q&A analysis (if sections available)
		question_density = 0.0
		answer_density = 0.0
		qa_differential = 0.0

		if sections and 'Q&A' in sections:
			# Simplified - would need more sophisticated Q&A parsing
			qa_text = sections.get('Q&A', sections.get('Questions and Answers', ''))
			if qa_text:
				qa_sentences = tokenize_sentences(qa_text)
				# Rough heuristic: questions have '?' and are typically lower density
				questions = [s for s in qa_sentences if '?' in s]
				answers = [s for s in qa_sentences if '?' not in s]

				if questions:
					question_density = np.mean([self._calculate_sentence_density(q) for q in questions])
				if answers:
					answer_density = np.mean([self._calculate_sentence_density(a) for a in answers])

				qa_differential = answer_density - question_density

		# Speaker analysis
		speaker_densities = {}
		if speakers:
			for speaker, text in speakers.items():
				speaker_sentences = tokenize_sentences(text)
				if speaker_sentences:
					densities_list = [self._calculate_sentence_density(s) for s in speaker_sentences]
					speaker_densities[speaker] = np.mean(densities_list)

		# Variance analysis
		mean_density = sentence_metrics.mean_numeric_density
		std_density = sentence_metrics.std_numeric_density
		variance_ratio = std_density / mean_density if mean_density > 0 else 0.0
		cv = std_density / mean_density if mean_density > 0 else 0.0

		return DistributionPattern(
			beginning_density=beginning_density,
			middle_density=middle_density,
			end_density=end_density,
			pattern_type=pattern_type,
			pattern_confidence=pattern_confidence,
			cluster_count=len(clusters),
			cluster_positions=clusters,
			cluster_densities=cluster_densities,
			question_avg_density=question_density,
			answer_avg_density=answer_density,
			qa_density_differential=qa_differential,
			speaker_densities=speaker_densities,
			density_variance_ratio=variance_ratio,
			coefficient_of_variation=cv
		)

	def calculate_informativeness(
		self,
		sentence_metrics: SentenceDensityMetrics,
		numerical_scores: 'NumericalScores',  # From existing transparency.py
		distribution: DistributionPattern
	) -> InformativenessMetrics:
		"""
		Calculate informativeness metrics based on numeric patterns

		Theory: Higher numeric density + better contextualization +
				forward-looking guidance = more informative call

		Args:
			sentence_metrics: Sentence-level density metrics
			numerical_scores: Existing numerical transparency scores
			distribution: Distribution pattern analysis

		Returns:
			InformativenessMetrics
		"""
		# Numeric Inclusion Ratio: % of all sentences that contain numbers
		# This measures the prevalence of numeric content across the entire transcript.
		# Since sentences are classified as dense/moderate/sparse (numeric) or narrative (non-numeric),
		# this ratio reflects what proportion of the call includes quantitative information.
		numeric_sentences = (
			sentence_metrics.numeric_dense_sentences +
			sentence_metrics.numeric_moderate_sentences +
			sentence_metrics.numeric_sparse_sentences
		)

		numeric_inclusion_ratio = numeric_sentences / sentence_metrics.total_sentences if sentence_metrics.total_sentences > 0 else 0.0

		# Get guidance and results density from existing scores
		guidance_density = numerical_scores.forward_looking_density
		results_density = numerical_scores.backward_looking_density

		# Specificity-weighted NIR
		specificity_index = numerical_scores.numerical_specificity_index
		specificity_weighted_nir = numeric_inclusion_ratio * (specificity_index / 2.0)

		# Informativeness score components (0-100 scale):
		# 1. Numeric density (30%) - more numbers generally = more informative
		density_component = min(sentence_metrics.mean_numeric_density / 10.0, 1.0) * 30

		# 2. Specificity (25%) - precise numbers more informative
		specificity_component = (specificity_index / 2.0) * 25

		# 3. Forward-looking density (25%) - guidance is highly informative
		guidance_component = min(guidance_density / 5.0, 1.0) * 25

		# 4. Contextualization (20%) - explained numbers more useful
		context_component = numerical_scores.contextualization_quality_score * 20

		informativeness_score = (
			density_component +
			specificity_component +
			guidance_component +
			context_component
		)

		# Forecast relevance: emphasis on forward-looking numeric content
		forecast_relevance_score = (
			guidance_density * 40 +  # High weight on guidance density
			(numerical_scores.forward_to_backward_ratio / 3.0) * 20 +  # Balance toward future
			specificity_component +  # Precise forecasts better
			context_component  # Explained forecasts more credible
		)
		forecast_relevance_score = min(forecast_relevance_score, 100)

		# Strategic insight classification
		if informativeness_score >= 75:
			quantitative_level = "very_high"
		elif informativeness_score >= 60:
			quantitative_level = "high"
		elif informativeness_score >= 40:
			quantitative_level = "medium"
		elif informativeness_score >= 25:
			quantitative_level = "low"
		else:
			quantitative_level = "very_low"

		# Transparency tier (based on percentiles)
		transparency_tier = self._classify_transparency_tier(informativeness_score)

		# Risk assessment: low numeric content may indicate evasion
		# Baseline: expect at least 3.5% transparency (S&P 500 benchmark)
		numeric_avoidance_risk = max(0, (3.5 - sentence_metrics.mean_numeric_density) * 20)
		numeric_avoidance_risk = min(numeric_avoidance_risk, 100)

		# Vagueness penalty: low specificity reduces informativeness
		vagueness_penalty = max(0, (1.0 - specificity_index / 2.0)) * 50

		# Contextualization score from existing analysis
		context_score = numerical_scores.contextualization_quality_score

		# Benchmark comparison (using 50 as median informativeness score)
		vs_sp500 = "above" if informativeness_score > 50 else ("at" if informativeness_score >= 45 else "below")

		return InformativenessMetrics(
			numeric_inclusion_ratio=numeric_inclusion_ratio,
			guidance_numeric_density=guidance_density,
			results_numeric_density=results_density,
			specificity_weighted_nir=specificity_weighted_nir,
			informativeness_score=informativeness_score,
			forecast_relevance_score=forecast_relevance_score,
			quantitative_disclosure_level=quantitative_level,
			transparency_tier=transparency_tier,
			numeric_avoidance_risk=numeric_avoidance_risk,
			vagueness_penalty=vagueness_penalty,
			contextualization_score=context_score,
			vs_sp500_informativeness=vs_sp500
		)

	def _calculate_sentence_density(self, sentence: str) -> float:
		"""
		Calculate numeric density for a single sentence

		Returns:
			Percentage of words that are numbers (0-100)
		"""
		words = tokenize_words(sentence, lowercase=False, remove_punct=True)
		if not words:
			return 0.0

		numbers = extract_numerical_tokens(sentence)
		density = (len(numbers) / len(words)) * 100

		return density

	def _classify_pattern(
		self,
		beginning: float,
		middle: float,
		end: float,
		all_densities: List[float]
	) -> Tuple[str, float]:
		"""
		Classify the distribution pattern

		Returns:
			(pattern_type, confidence)
		"""
		# Thresholds for classification
		significant_diff = 3.0  # % points difference

		# Calculate differences
		begin_vs_middle = beginning - middle
		end_vs_middle = end - middle
		begin_vs_end = beginning - end

		# Check for uniform distribution (low variance)
		std = np.std(all_densities)
		mean = np.mean(all_densities)
		cv = std / mean if mean > 0 else 0

		if cv < 0.3:
			return "uniform", 0.9

		# Front-loaded: high at beginning, lower later
		if begin_vs_middle > significant_diff and begin_vs_end > significant_diff:
			confidence = min(begin_vs_middle / 10.0, 1.0)
			return "front-loaded", confidence

		# Back-loaded: high at end, lower earlier
		if end_vs_middle > significant_diff and end_vs_middle > -begin_vs_middle:
			confidence = min(end_vs_middle / 10.0, 1.0)
			return "back-loaded", confidence

		# Clustered: high variance with distinct peaks
		if cv > 0.7:
			return "clustered", 0.8

		# Scattered: moderate variance, no clear pattern
		return "scattered", 0.6

	def _identify_clusters(
		self,
		densities: List[float]
	) -> Tuple[List[Tuple[int, int]], List[float]]:
		"""
		Identify high-density clusters using rolling window

		Returns:
			(cluster_positions, cluster_densities)
		"""
		clusters = []
		cluster_densities = []

		if len(densities) < self.CLUSTER_WINDOW_SIZE:
			return clusters, cluster_densities

		# Rolling window approach
		window_size = self.CLUSTER_WINDOW_SIZE
		in_cluster = False
		cluster_start = 0

		for i in range(len(densities) - window_size + 1):
			window = densities[i:i + window_size]
			window_avg = np.mean(window)

			if window_avg >= self.CLUSTER_DENSITY_THRESHOLD:
				if not in_cluster:
					# Start new cluster
					cluster_start = i
					in_cluster = True
			else:
				if in_cluster:
					# End cluster
					cluster_end = i - 1 + window_size
					clusters.append((cluster_start, cluster_end))
					cluster_density = np.mean(densities[cluster_start:cluster_end])
					cluster_densities.append(cluster_density)
					in_cluster = False

		# Handle cluster extending to end
		if in_cluster:
			clusters.append((cluster_start, len(densities) - 1))
			cluster_densities.append(np.mean(densities[cluster_start:]))

		return clusters, cluster_densities

	def _classify_transparency_tier(self, score: float) -> str:
		"""Classify transparency tier based on score"""
		if score >= 70:
			return "top_quartile"
		elif score >= 55:
			return "above_average"
		elif score >= 40:
			return "average"
		elif score >= 25:
			return "below_average"
		else:
			return "bottom_quartile"

	def _empty_sentence_metrics(self) -> SentenceDensityMetrics:
		"""Return empty metrics for edge cases"""
		return SentenceDensityMetrics(
			total_sentences=0,
			numeric_dense_sentences=0,
			numeric_moderate_sentences=0,
			numeric_sparse_sentences=0,
			narrative_sentences=0,
			mean_numeric_density=0.0,
			median_numeric_density=0.0,
			std_numeric_density=0.0,
			max_numeric_density=0.0,
			min_numeric_density=0.0,
			p25_density=0.0,
			p75_density=0.0,
			proportion_numeric_dense=0.0,
			proportion_narrative=0.0,
			top_dense_sentences=[],
			density_by_position=[]
		)

	def generate_ascii_heatmap(self, distribution: DistributionPattern, sentence_metrics: SentenceDensityMetrics) -> str:
		"""
		Generate ASCII heatmap visualization of density distribution

		Returns:
			Multi-line string with ASCII heatmap
		"""
		lines = []
		lines.append("="*60)
		lines.append("NUMERIC DENSITY DISTRIBUTION HEATMAP")
		lines.append("="*60)
		lines.append("")

		# Overall pattern
		lines.append(f"Pattern Type: {distribution.pattern_type.upper()} (confidence: {distribution.pattern_confidence:.1%})")
		lines.append("")

		# Positional distribution
		lines.append("Distribution by Position:")
		lines.append(f"  Beginning (first 20%):  {self._density_bar(distribution.beginning_density, 50)} {distribution.beginning_density:.1f}%")
		lines.append(f"  Middle (60%):          {self._density_bar(distribution.middle_density, 50)} {distribution.middle_density:.1f}%")
		lines.append(f"  End (last 20%):        {self._density_bar(distribution.end_density, 50)} {distribution.end_density:.1f}%")
		lines.append("")

		# Clusters
		if distribution.cluster_count > 0:
			lines.append(f"High-Density Clusters: {distribution.cluster_count}")
			for i, (start, end) in enumerate(distribution.cluster_positions[:5], 1):
				density = distribution.cluster_densities[i-1]
				lines.append(f"  Cluster {i}: Sentences {start}-{end} (avg density: {density:.1f}%)")
			if distribution.cluster_count > 5:
				lines.append(f"  ... and {distribution.cluster_count - 5} more clusters")
			lines.append("")

		# Q&A differential
		if distribution.qa_density_differential != 0.0:
			lines.append("Q&A Analysis:")
			lines.append(f"  Questions: {distribution.question_avg_density:.1f}%")
			lines.append(f"  Answers:   {distribution.answer_avg_density:.1f}%")
			lines.append(f"  Differential: {distribution.qa_density_differential:+.1f}% {'(answers more numeric)' if distribution.qa_density_differential > 0 else '(questions more numeric)'}")
			lines.append("")

		# Speaker breakdown
		if distribution.speaker_densities:
			lines.append("Density by Speaker:")
			for speaker, density in sorted(distribution.speaker_densities.items(), key=lambda x: x[1], reverse=True)[:5]:
				lines.append(f"  {speaker:30} {self._density_bar(density, 30)} {density:.1f}%")
			lines.append("")

		lines.append("="*60)

		return "\n".join(lines)

	def _density_bar(self, density: float, max_width: int = 40) -> str:
		"""Generate ASCII bar for density visualization"""
		# Normalize to max_width (assuming max density of 20%)
		max_density = 20.0
		width = int((density / max_density) * max_width)
		width = min(width, max_width)

		bar = "█" * width
		empty = "░" * (max_width - width)

		return f"[{bar}{empty}]"

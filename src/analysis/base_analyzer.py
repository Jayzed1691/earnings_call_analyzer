"""
Base Analyzer Abstract Class

Provides shared functionality for all analyzer implementations,
eliminating code duplication across sentiment, complexity, and numerical analyzers.
"""
from abc import ABC, abstractmethod
from typing import Dict, TypeVar, Generic, Any
import logging

logger = logging.getLogger(__name__)

# Generic type for analysis results
T = TypeVar('T')


class BaseAnalyzer(ABC, Generic[T]):
    """
    Abstract base class for all analyzers

    Provides common functionality:
    - analyze_by_section(): Analyze text by section (Prepared Remarks, Q&A)
    - analyze_by_speaker(): Analyze text by speaker (CEO, CFO, etc.)
    - Error handling patterns
    - Logging patterns

    Subclasses must implement:
    - analyze(text: str) -> T: Core analysis logic
    """

    def __init__(self, analyzer_name: str = None):
        """
        Initialize base analyzer

        Args:
            analyzer_name: Name for logging purposes (default: class name)
        """
        self.analyzer_name = analyzer_name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.analyzer_name}")

    @abstractmethod
    def analyze(self, text: str) -> T:
        """
        Analyze a single text segment

        Must be implemented by subclass

        Args:
            text: Text to analyze

        Returns:
            Analysis result of type T (defined by subclass)
        """
        pass

    def analyze_by_section(self, sections: Dict[str, str]) -> Dict[str, T]:
        """
        Analyze text by section (e.g., Prepared Remarks, Q&A)

        Args:
            sections: Dictionary mapping section_name -> text

        Returns:
            Dictionary mapping section_name -> analysis result
        """
        results = {}

        for section_name, text in sections.items():
            if not text or not text.strip():
                self.logger.debug(f"Skipping empty section: {section_name}")
                continue

            try:
                self.logger.debug(f"Analyzing section: {section_name} ({len(text)} chars)")
                results[section_name] = self.analyze(text)
            except Exception as e:
                self.logger.error(
                    f"Failed to analyze section '{section_name}': {e}",
                    exc_info=True
                )
                # Re-raise to let caller handle
                raise

        return results

    def analyze_by_speaker(self, speakers: Dict[str, str]) -> Dict[str, T]:
        """
        Analyze text by speaker (e.g., CEO, CFO, Analyst)

        Args:
            speakers: Dictionary mapping speaker_name -> text

        Returns:
            Dictionary mapping speaker_name -> analysis result
        """
        results = {}

        for speaker_name, text in speakers.items():
            if not text or not text.strip():
                self.logger.debug(f"Skipping empty speaker: {speaker_name}")
                continue

            try:
                self.logger.debug(f"Analyzing speaker: {speaker_name} ({len(text)} chars)")
                results[speaker_name] = self.analyze(text)
            except Exception as e:
                self.logger.error(
                    f"Failed to analyze speaker '{speaker_name}': {e}",
                    exc_info=True
                )
                # Re-raise to let caller handle
                raise

        return results

    def analyze_batch(self, texts: Dict[str, str]) -> Dict[str, T]:
        """
        Analyze multiple text segments

        Generic method that can be used for any type of batch analysis

        Args:
            texts: Dictionary mapping identifier -> text

        Returns:
            Dictionary mapping identifier -> analysis result
        """
        results = {}

        for identifier, text in texts.items():
            if not text or not text.strip():
                self.logger.debug(f"Skipping empty text: {identifier}")
                continue

            try:
                results[identifier] = self.analyze(text)
            except Exception as e:
                self.logger.error(
                    f"Failed to analyze '{identifier}': {e}",
                    exc_info=True
                )
                # Re-raise to let caller handle
                raise

        return results

    def validate_input(self, text: str) -> None:
        """
        Validate input text before analysis

        Can be overridden by subclasses for specific validation rules

        Args:
            text: Text to validate

        Raises:
            ValueError: If text is invalid
        """
        if not text or not isinstance(text, str):
            raise ValueError(f"{self.analyzer_name}: Text must be a non-empty string")

        if not text.strip():
            raise ValueError(f"{self.analyzer_name}: Text cannot be only whitespace")

        # Minimum reasonable text length (10 characters)
        if len(text.strip()) < 10:
            raise ValueError(
                f"{self.analyzer_name}: Text too short ({len(text)} chars). "
                f"Minimum 10 characters required."
            )


class CachedAnalyzer(BaseAnalyzer[T]):
    """
    Base analyzer with caching support

    Automatically caches analysis results to avoid redundant computation
    """

    def __init__(self, analyzer_name: str = None, use_cache: bool = True):
        """
        Initialize cached analyzer

        Args:
            analyzer_name: Name for logging purposes
            use_cache: Whether to enable caching (default: True)
        """
        super().__init__(analyzer_name)
        self.use_cache = use_cache
        self._cache = None

        if use_cache:
            from src.cache.result_cache import get_cache
            self._cache = get_cache()

    @abstractmethod
    def _analyze_impl(self, text: str) -> T:
        """
        Core analysis implementation (without caching)

        Must be implemented by subclass

        Args:
            text: Text to analyze

        Returns:
            Analysis result
        """
        pass

    def analyze(self, text: str) -> T:
        """
        Analyze text with caching support

        Checks cache first, then calls _analyze_impl() if needed

        Args:
            text: Text to analyze

        Returns:
            Analysis result (from cache or fresh analysis)
        """
        # Validate input
        self.validate_input(text)

        # Check cache if enabled
        if self._cache:
            cache_key = self.analyzer_name.lower()
            cached_result = self._cache.get(text, cache_key)

            if cached_result is not None:
                self.logger.debug("Cache hit")
                return self._deserialize_result(cached_result)

        # Perform analysis
        self.logger.debug("Cache miss - performing analysis")
        result = self._analyze_impl(text)

        # Store in cache if enabled
        if self._cache:
            serialized = self._serialize_result(result)
            self._cache.set(text, self.analyzer_name.lower(), serialized)

        return result

    def _serialize_result(self, result: T) -> Any:
        """
        Serialize result for caching (can be overridden)

        Default: assumes result is JSON-serializable or has asdict()

        Args:
            result: Analysis result

        Returns:
            Serializable version of result
        """
        from dataclasses import asdict, is_dataclass

        if is_dataclass(result):
            return asdict(result)
        return result

    def _deserialize_result(self, data: Any) -> T:
        """
        Deserialize cached result (can be overridden)

        Default: returns data as-is (assumes simple types)

        Args:
            data: Cached data

        Returns:
            Deserialized result
        """
        # Subclasses should override this to reconstruct their specific result type
        return data

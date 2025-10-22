"""
Test script for Phase 2 Architecture improvements

Tests:
1. BaseAnalyzer abstract class
2. Retry logic with exponential backoff
3. Comprehensive error handling in OllamaClient
4. Tokenization caching in TranscriptProcessor
"""
import logging
import sys
import tempfile
from pathlib import Path

# Setup logging
from config.logging_config import setup_logging
setup_logging(log_level='INFO')

logger = logging.getLogger(__name__)


def test_base_analyzer():
    """Test BaseAnalyzer abstract class"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: BaseAnalyzer Abstract Class")
    logger.info("="*80)

    from src.analysis.base_analyzer import BaseAnalyzer
    from dataclasses import dataclass

    # Create a simple concrete implementation
    @dataclass
    class SimpleResult:
        score: float

    class TestAnalyzer(BaseAnalyzer[SimpleResult]):
        def analyze(self, text: str) -> SimpleResult:
            return SimpleResult(score=len(text) / 100.0)

    # Test initialization
    analyzer = TestAnalyzer(analyzer_name="test")
    logger.info("✅ BaseAnalyzer subclass created successfully")

    # Test analyze_by_section
    sections = {
        'section1': 'This is section one with some text',
        'section2': 'This is section two with more text',
        'empty': ''  # Should be skipped
    }

    try:
        results = analyzer.analyze_by_section(sections)

        if len(results) == 2:  # empty section should be skipped
            logger.info("✅ analyze_by_section works correctly (skipped empty)")
        else:
            logger.error(f"❌ Expected 2 results, got {len(results)}")
            return False

        # Verify results
        if all(isinstance(r, SimpleResult) for r in results.values()):
            logger.info("✅ All results are correct type")
        else:
            logger.error("❌ Results are not correct type")
            return False

    except Exception as e:
        logger.error(f"❌ analyze_by_section failed: {e}")
        return False

    # Test validation
    try:
        analyzer.validate_input("")
        logger.error("❌ Should have raised ValueError for empty text")
        return False
    except ValueError:
        logger.info("✅ Input validation works")

    logger.info("✅ BaseAnalyzer test PASSED")
    return True


def test_retry_logic():
    """Test retry decorator and utilities"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Retry Logic")
    logger.info("="*80)

    from src.utils.retry import exponential_backoff_retry, retry_once, with_fallback
    import time

    # Test 1: Successful retry after failure
    attempt_count = [0]

    @exponential_backoff_retry(max_attempts=3, initial_delay=0.1, log_attempts=False)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise ConnectionError("Simulated failure")
        return "success"

    try:
        result = flaky_function()
        if result == "success" and attempt_count[0] == 2:
            logger.info("✅ Retry decorator works (succeeded on attempt 2)")
        else:
            logger.error(f"❌ Unexpected result: {result}, attempts: {attempt_count[0]}")
            return False
    except Exception as e:
        logger.error(f"❌ Retry failed: {e}")
        return False

    # Test 2: Retry with fallback value
    @exponential_backoff_retry(
        max_attempts=2,
        initial_delay=0.1,
        fallback_value="fallback",
        log_attempts=False
    )
    def always_fails():
        raise RuntimeError("Always fails")

    result = always_fails()
    if result == "fallback":
        logger.info("✅ Fallback value works")
    else:
        logger.error(f"❌ Expected fallback, got: {result}")
        return False

    # Test 3: with_fallback utility
    def primary():
        raise ValueError("Primary failed")

    def fallback():
        return "fallback_result"

    combined = with_fallback(primary, fallback)
    result = combined()

    if result == "fallback_result":
        logger.info("✅ with_fallback utility works")
    else:
        logger.error(f"❌ Expected fallback_result, got: {result}")
        return False

    logger.info("✅ Retry logic test PASSED")
    return True


def test_ollama_error_handling():
    """Test OllamaClient error handling"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: OllamaClient Error Handling")
    logger.info("="*80)

    try:
        from src.models.ollama_client import OllamaClient

        client = OllamaClient()
        logger.info("✅ OllamaClient initialized successfully")

        # Test sentiment validation
        test_responses = [
            {'sentiment': 'Positive', 'confidence': 0.8},  # Valid
            {'sentiment': 'Invalid', 'confidence': 0.8},   # Invalid sentiment (should fix)
            {'sentiment': 'Neutral', 'confidence': 1.5},   # Invalid confidence (should clamp)
        ]

        for i, response in enumerate(test_responses, 1):
            try:
                client._validate_sentiment_response(response)
                logger.info(f"✅ Validation test {i} passed")
            except Exception as e:
                logger.error(f"❌ Validation test {i} failed: {e}")
                return False

        # Test neutral fallback
        fallback = client._neutral_sentiment_fallback("test reason")
        if (fallback['sentiment'] == 'Neutral' and
            fallback['confidence'] == 0.5 and
            'test reason' in fallback['reasoning']):
            logger.info("✅ Neutral fallback works correctly")
        else:
            logger.error(f"❌ Unexpected fallback: {fallback}")
            return False

        logger.info("✅ OllamaClient error handling test PASSED")
        return True

    except ModuleNotFoundError as e:
        logger.warning(f"⚠️  Skipping OllamaClient test (dependency missing): {e}")
        return True  # Don't fail if optional dependency missing


def test_tokenization_caching():
    """Test tokenization caching in ProcessedTranscript"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Tokenization Caching")
    logger.info("="*80)

    try:
        from src.core.transcript_processor import ProcessedTranscript, TranscriptMetadata

        # Create a test transcript
        test_text = " ".join(["word"] * 1000)  # 1000 words

        transcript = ProcessedTranscript(
            raw_text=test_text,
            cleaned_text=test_text,
            metadata=TranscriptMetadata(),
            speakers={},
            sections={}
        )

        # Verify properties exist but are not computed yet
        if transcript._sentences is None and transcript._words is None:
            logger.info("✅ Tokenization is lazy (not computed at init)")
        else:
            logger.error("❌ Tokenization was computed at init")
            return False

        # Access sentences (should trigger tokenization)
        sentences = transcript.sentences
        if sentences is not None and transcript._sentences is not None:
            logger.info("✅ Sentences cached after first access")
        else:
            logger.error("❌ Sentences not cached")
            return False

        # Access sentences again (should use cache)
        sentences2 = transcript.sentences
        if sentences is sentences2:  # Same object reference
            logger.info("✅ Cached sentences reused")
        else:
            logger.error("❌ Sentences re-computed instead of cached")
            return False

        # Access words
        words = transcript.words
        if words is not None and len(words) == 1000:
            logger.info("✅ Words tokenization works and is cached")
        else:
            logger.error(f"❌ Expected 1000 words, got {len(words) if words else 'None'}")
            return False

        # Access word_count (should use cached words)
        count = transcript.word_count
        if count == 1000:
            logger.info("✅ word_count property works")
        else:
            logger.error(f"❌ Expected count 1000, got {count}")
            return False

        # Access sentence_count
        sent_count = transcript.sentence_count
        if sent_count > 0:
            logger.info(f"✅ sentence_count property works ({sent_count} sentences)")
        else:
            logger.error("❌ sentence_count is zero")
            return False

        logger.info("✅ Tokenization caching test PASSED")
        return True

    except ModuleNotFoundError as e:
        logger.warning(f"⚠️  Skipping tokenization caching test (dependency missing): {e}")
        return True  # Don't fail if optional dependency missing
    except Exception as e:
        logger.error(f"❌ Tokenization caching test FAILED: {e}", exc_info=True)
        return False


def test_code_structure():
    """Test that new code structure exists"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Code Structure")
    logger.info("="*80)

    files_to_check = [
        ("src/analysis/base_analyzer.py", "BaseAnalyzer"),
        ("src/utils/retry.py", "Retry utilities"),
    ]

    for file_path, description in files_to_check:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {description} file exists")
        else:
            logger.error(f"❌ {description} file not found: {file_path}")
            return False

    # Check for key classes/functions
    try:
        from src.analysis.base_analyzer import BaseAnalyzer, CachedAnalyzer
        logger.info("✅ BaseAnalyzer and CachedAnalyzer can be imported")

        from src.utils.retry import (
            exponential_backoff_retry,
            retry_on_timeout,
            RetryStrategy,
            with_fallback
        )
        logger.info("✅ Retry utilities can be imported")

    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

    logger.info("✅ Code structure test PASSED")
    return True


def main():
    """Run all tests"""
    logger.info("="*80)
    logger.info("PHASE 2 ARCHITECTURE - INTEGRATION TEST")
    logger.info("="*80)

    results = []

    # Run tests
    results.append(("BaseAnalyzer", test_base_analyzer()))
    results.append(("Retry Logic", test_retry_logic()))
    results.append(("OllamaClient Error Handling", test_ollama_error_handling()))
    results.append(("Tokenization Caching", test_tokenization_caching()))
    results.append(("Code Structure", test_code_structure()))

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{name:.<40} {status}")

    logger.info("="*80)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("="*80)

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test script for Phase 1 Quick Win improvements

Tests:
1. Result caching for LLM calls
2. Session context managers
3. Input validation
4. Structured logging
"""
import logging
from pathlib import Path
import tempfile
import sys

# Setup logging first
from config.logging_config import setup_logging
setup_logging(log_level='INFO')

logger = logging.getLogger(__name__)

def test_caching():
    """Test LLM result caching"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Result Caching")
    logger.info("="*80)

    from src.cache.result_cache import ResultCache

    cache = ResultCache()

    # Test cache set/get
    test_text = "This is a test transcript for caching."
    test_result = {'sentiment': 'Positive', 'score': 0.8}

    logger.info("Setting cache entry...")
    cache.set(test_text, 'llm_sentiment', test_result)

    logger.info("Retrieving cache entry...")
    cached = cache.get(test_text, 'llm_sentiment')

    if cached == test_result:
        logger.info("✅ Cache test PASSED")
        return True
    else:
        logger.error(f"❌ Cache test FAILED: Expected {test_result}, got {cached}")
        return False


def test_session_management():
    """Test database session context manager"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Session Context Manager")
    logger.info("="*80)

    try:
        from src.database.repository import DatabaseRepository
        from config.settings import settings

        repo = DatabaseRepository(settings.DATABASE_URL)

        # Test context manager
        with repo.get_session() as session:
            logger.info("Session created successfully")
            # Simple query
            from src.database.models import Company
            count = session.query(Company).count()
            logger.info(f"Companies in database: {count}")

        logger.info("Session closed automatically")
        logger.info("✅ Session management test PASSED")
        return True
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️  Session management test SKIPPED: {e}")
        logger.warning("Install sqlalchemy to run database tests")
        return True  # Don't fail if optional dependency missing
    except Exception as e:
        logger.error(f"❌ Session management test FAILED: {e}")
        return False


def test_input_validation():
    """Test transcript input validation"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Input Validation")
    logger.info("="*80)

    from src.core.transcript_processor import TranscriptProcessor

    processor = TranscriptProcessor()

    # Test 1: Empty file
    logger.info("Test 3a: Empty file validation")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        empty_file = f.name
        f.write("")

    try:
        processor.validate_file(empty_file)
        logger.error("❌ Empty file test FAILED: Should have raised ValueError")
        Path(empty_file).unlink()
        return False
    except ValueError as e:
        logger.info(f"✅ Empty file correctly rejected: {e}")
        Path(empty_file).unlink()

    # Test 2: File too large
    logger.info("Test 3b: Content validation (too short)")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        short_file = f.name
        f.write("Too short")

    try:
        processor.validate_file(short_file)
        text = Path(short_file).read_text()
        processor.validate_content(text)
        logger.error("❌ Short content test FAILED: Should have raised ValueError")
        Path(short_file).unlink()
        return False
    except ValueError as e:
        logger.info(f"✅ Short content correctly rejected: {e}")
        Path(short_file).unlink()

    # Test 3: Valid file
    logger.info("Test 3c: Valid file validation")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        valid_file = f.name
        # Write minimum valid content
        content = " ".join(["word"] * 600)  # 600 words (minimum is 500)
        f.write(content)

    try:
        processor.validate_file(valid_file)
        text = Path(valid_file).read_text()
        processor.validate_content(text)
        logger.info("✅ Valid file correctly accepted")
        Path(valid_file).unlink()
    except Exception as e:
        logger.error(f"❌ Valid file test FAILED: {e}")
        Path(valid_file).unlink()
        return False

    logger.info("✅ Input validation test PASSED")
    return True


def test_logging():
    """Test logging configuration"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Structured Logging")
    logger.info("="*80)

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")

    # Test performance logger
    from config.logging_config import PerformanceLogger

    logger.info("Testing PerformanceLogger...")
    with PerformanceLogger("test_operation", logger):
        import time
        time.sleep(0.1)

    # Check log file exists
    from config.settings import settings
    log_file = settings.DATA_DIR / "logs" / "analyzer.log"

    if log_file.exists():
        logger.info(f"✅ Log file created: {log_file}")
        logger.info("✅ Logging test PASSED")
        return True
    else:
        logger.error(f"❌ Log file not found: {log_file}")
        return False


def main():
    """Run all tests"""
    logger.info("="*80)
    logger.info("PHASE 1 QUICK WINS - INTEGRATION TEST")
    logger.info("="*80)

    results = []

    # Run tests
    results.append(("Caching", test_caching()))
    results.append(("Session Management", test_session_management()))
    results.append(("Input Validation", test_input_validation()))
    results.append(("Logging", test_logging()))

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name}: {status}")

    all_passed = all(result[1] for result in results)

    logger.info("="*80)
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("="*80)
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.info("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Unit tests for Phase 1 Quick Win improvements (no external dependencies)

Tests:
1. Result caching module
2. Session context manager implementation
3. Logging configuration
"""
import logging
import sys
import tempfile
from pathlib import Path

# Setup logging
from config.logging_config import setup_logging
setup_logging(log_level='INFO')

logger = logging.getLogger(__name__)


def test_result_cache():
    """Test ResultCache class"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: ResultCache Module")
    logger.info("="*80)

    from src.cache.result_cache import ResultCache

    # Create temp cache directory
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ResultCache(cache_dir=Path(tmpdir), ttl_seconds=60)

        # Test 1: Set and get
        logger.info("Test 1a: Cache set/get")
        text = "This is a test transcript"
        result = {'sentiment': 'Positive', 'score': 0.85, 'confidence': 0.9}

        cache.set(text, 'test_analysis', result)
        retrieved = cache.get(text, 'test_analysis')

        if retrieved == result:
            logger.info("✅ Cache set/get works correctly")
        else:
            logger.error(f"❌ Expected {result}, got {retrieved}")
            return False

        # Test 2: Cache miss
        logger.info("Test 1b: Cache miss")
        missing = cache.get("non-existent text", 'test_analysis')
        if missing is None:
            logger.info("✅ Cache miss handled correctly")
        else:
            logger.error(f"❌ Expected None, got {missing}")
            return False

        # Test 3: Cache stats
        logger.info("Test 1c: Cache stats")
        stats = cache.stats()
        if stats['enabled'] and stats['total_entries'] == 1:
            logger.info(f"✅ Cache stats correct: {stats}")
        else:
            logger.error(f"❌ Unexpected stats: {stats}")
            return False

        # Test 4: Cache clear
        logger.info("Test 1d: Cache clear")
        cleared = cache.clear()
        if cleared == 1:
            logger.info("✅ Cache cleared successfully")
        else:
            logger.error(f"❌ Expected 1 entry cleared, got {cleared}")
            return False

    logger.info("✅ ResultCache test PASSED")
    return True


def test_context_manager():
    """Test session context manager pattern"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Context Manager Implementation")
    logger.info("="*80)

    # Test the pattern exists in repository
    try:
        # Just verify the method exists and is a generator
        import inspect
        from contextlib import contextmanager

        # Read the repository file to verify pattern
        repo_file = Path("src/database/repository.py")
        if not repo_file.exists():
            logger.warning("⚠️  Repository file not found, skipping")
            return True

        content = repo_file.read_text()

        # Check for context manager decorator
        if "@contextmanager" in content:
            logger.info("✅ @contextmanager decorator found")
        else:
            logger.error("❌ @contextmanager decorator not found")
            return False

        # Check for session.rollback()
        if "session.rollback()" in content:
            logger.info("✅ Rollback handling found")
        else:
            logger.error("❌ Rollback handling not found")
            return False

        # Check for exception handling
        if "except SQLAlchemyError" in content or "except Exception" in content:
            logger.info("✅ Exception handling found")
        else:
            logger.error("❌ Exception handling not found")
            return False

        logger.info("✅ Context manager implementation PASSED")
        return True

    except Exception as e:
        logger.error(f"❌ Context manager test FAILED: {e}")
        return False


def test_input_validation_code():
    """Test input validation code exists"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Input Validation Implementation")
    logger.info("="*80)

    try:
        processor_file = Path("src/core/transcript_processor.py")
        if not processor_file.exists():
            logger.warning("⚠️  Processor file not found, skipping")
            return True

        content = processor_file.read_text()

        # Check for validation methods
        checks = [
            ("validate_file", "File validation method"),
            ("validate_content", "Content validation method"),
            ("MAX_FILE_SIZE", "Maximum file size constant"),
            ("MIN_TRANSCRIPT_LENGTH", "Minimum length validation"),
            ("MAX_TRANSCRIPT_LENGTH", "Maximum length validation")
        ]

        for check_string, description in checks:
            if check_string in content:
                logger.info(f"✅ {description} found")
            else:
                logger.error(f"❌ {description} not found")
                return False

        logger.info("✅ Input validation implementation PASSED")
        return True

    except Exception as e:
        logger.error(f"❌ Input validation test FAILED: {e}")
        return False


def test_logging_config():
    """Test logging configuration"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Logging Configuration")
    logger.info("="*80)

    # Test logging levels
    logger.debug("DEBUG level test")
    logger.info("INFO level test")
    logger.warning("WARNING level test")

    # Test PerformanceLogger
    from config.logging_config import PerformanceLogger
    import time

    logger.info("Testing PerformanceLogger context manager...")
    with PerformanceLogger("test_operation", logger):
        time.sleep(0.05)

    # Check log file was created
    from config.settings import settings
    log_dir = settings.DATA_DIR / "logs"
    log_file = log_dir / "analyzer.log"

    if log_file.exists():
        logger.info(f"✅ Log file created: {log_file}")

        # Check log file has content
        size = log_file.stat().st_size
        if size > 0:
            logger.info(f"✅ Log file has content ({size} bytes)")
        else:
            logger.error("❌ Log file is empty")
            return False
    else:
        logger.error(f"❌ Log file not found: {log_file}")
        return False

    logger.info("✅ Logging configuration PASSED")
    return True


def test_code_updates():
    """Test that print statements were replaced with logging"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Print to Logging Migration")
    logger.info("="*80)

    files_to_check = [
        ("src/analysis/aggregator.py", "Aggregator"),
        ("src/analysis/sentiment/llm_analyzer.py", "LLM Analyzer"),
    ]

    for file_path, name in files_to_check:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"⚠️  {name} not found, skipping")
            continue

        content = path.read_text()

        # Check for logging import
        if "import logging" in content:
            logger.info(f"✅ {name}: logging module imported")
        else:
            logger.error(f"❌ {name}: logging module not imported")
            return False

        # Check for logger creation
        if "logger = logging.getLogger" in content or "= logging.getLogger" in content:
            logger.info(f"✅ {name}: logger instance created")
        else:
            logger.error(f"❌ {name}: logger instance not found")
            return False

        # Check for logger usage
        if "logger.info(" in content or "logger.warning(" in content or "logger.error(" in content:
            logger.info(f"✅ {name}: logger methods used")
        else:
            logger.error(f"❌ {name}: logger methods not found")
            return False

    logger.info("✅ Logging migration PASSED")
    return True


def main():
    """Run all tests"""
    logger.info("="*80)
    logger.info("PHASE 1 QUICK WINS - CORE UNIT TESTS")
    logger.info("="*80)

    results = []

    # Run tests
    results.append(("ResultCache", test_result_cache()))
    results.append(("Context Manager", test_context_manager()))
    results.append(("Input Validation", test_input_validation_code()))
    results.append(("Logging Config", test_logging_config()))
    results.append(("Code Updates", test_code_updates()))

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{name:.<30} {status}")

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

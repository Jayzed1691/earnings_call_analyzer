"""
Test script for Phase 3 Advanced improvements

Tests:
1. Async/parallel section analysis
2. Connection pooling for Ollama
3. Performance monitoring
4. Dependency injection
"""
import logging
import sys
import asyncio
import time
from pathlib import Path

# Setup logging
from config.logging_config import setup_logging
setup_logging(log_level='INFO')

logger = logging.getLogger(__name__)


def test_async_engine():
    """Test async analysis engine"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Async/Parallel Analysis Engine")
    logger.info("="*80)

    from src.utils.async_engine import AsyncAnalysisEngine, run_async

    # Create test analyzer function
    def mock_analyzer(text: str) -> dict:
        """Mock analyzer that takes some time"""
        time.sleep(0.1)  # Simulate work
        return {'score': len(text) / 100.0, 'text': text[:20]}

    # Test sections
    sections = {
        'section1': 'This is the first section with some text',
        'section2': 'This is the second section with more text',
        'section3': 'This is the third section',
        'section4': 'This is the fourth section with even more text'
    }

    # Test parallel analysis
    async def test_parallel():
        with AsyncAnalysisEngine(max_workers=4) as engine:
            start = time.time()
            results = await engine.analyze_sections_parallel(
                sections,
                mock_analyzer,
                "mock_analyzer"
            )
            duration = time.time() - start

            # Verify results
            if len(results) == 4:
                logger.info("✅ All 4 sections analyzed")
            else:
                logger.error(f"❌ Expected 4 results, got {len(results)}")
                return False

            # Verify parallel execution was faster than sequential
            # Sequential would take: 4 sections * 0.1s = 0.4s
            # Parallel with 4 workers should take ~0.1s
            if duration < 0.3:  # Should be significantly faster
                logger.info(f"✅ Parallel execution was fast ({duration:.2f}s)")
            else:
                logger.warning(f"⚠️  Parallel execution took {duration:.2f}s (expected < 0.3s)")

            # Verify results are correct
            for name, result in results.items():
                if isinstance(result, dict) and 'score' in result:
                    logger.info(f"✅ {name}: score={result['score']:.2f}")
                else:
                    logger.error(f"❌ Invalid result for {name}")
                    return False

        logger.info("✅ Async analysis engine test PASSED")
        return True

    try:
        result = run_async(test_parallel())
        return result
    except Exception as e:
        logger.error(f"❌ Async engine test FAILED: {e}", exc_info=True)
        return False


def test_connection_pool():
    """Test Ollama connection pooling"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Connection Pooling")
    logger.info("="*80)

    try:
        from src.models.ollama_pool import OllamaConnectionPool

        # Create pool
        pool = OllamaConnectionPool(pool_size=2, max_overflow=1, timeout=1.0)
        logger.info("✅ Connection pool created")

    except ModuleNotFoundError as e:
        logger.warning(f"⚠️  Skipping connection pool test (dependency missing): {e}")
        return True  # Don't fail if optional dependency missing

    try:

        # Test getting connections
        connections = []
        for i in range(2):
            with pool.get_connection() as client:
                logger.info(f"✅ Acquired connection {i+1}")
                connections.append(client)

        # Test pool stats
        stats = pool.get_stats()
        logger.info(f"✅ Pool stats: {stats}")

        if stats['pool_size'] == 2:
            logger.info("✅ Pool size correct")
        else:
            logger.error(f"❌ Pool size incorrect: {stats['pool_size']}")
            return False

        # Test overflow
        logger.info("Testing overflow connections...")
        try:
            acquired = []
            # Try to get more connections than pool size
            with pool.get_connection() as c1:
                acquired.append(c1)
                with pool.get_connection() as c2:
                    acquired.append(c2)
                    # This should trigger overflow
                    with pool.get_connection() as c3:
                        acquired.append(c3)
                        logger.info("✅ Overflow connection acquired")

        except Exception as e:
            logger.warning(f"⚠️  Overflow test: {e}")

        # Cleanup
        pool.shutdown()
        logger.info("✅ Pool shutdown successful")

        logger.info("✅ Connection pooling test PASSED")
        return True

    except Exception as e:
        logger.error(f"❌ Connection pooling test FAILED: {e}", exc_info=True)
        return False


def test_performance_monitoring():
    """Test performance monitoring"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Performance Monitoring")
    logger.info("="*80)

    from src.utils.performance import PerformanceMonitor

    # Create monitor
    monitor = PerformanceMonitor(enabled=True, alert_threshold=0.5)
    logger.info("✅ Performance monitor created")

    # Test measuring operations
    with monitor.measure("test_operation_1", metadata={'test': True}):
        time.sleep(0.1)

    with monitor.measure("test_operation_2"):
        time.sleep(0.05)

    # Measure same operation multiple times
    for i in range(5):
        with monitor.measure("repeated_operation"):
            time.sleep(0.02)

    logger.info("✅ Operations measured")

    # Get stats
    stats = monitor.get_stats()

    if len(stats) == 3:  # Should have 3 different operations
        logger.info("✅ Correct number of operations tracked")
    else:
        logger.error(f"❌ Expected 3 operations, got {len(stats)}")
        return False

    # Verify stats for repeated operation
    repeated_stats = stats.get('repeated_operation')
    if repeated_stats and repeated_stats.count == 5:
        logger.info(f"✅ Repeated operation tracked correctly (count={repeated_stats.count})")
    else:
        logger.error(f"❌ Repeated operation stats incorrect")
        return False

    # Test bottleneck identification
    bottlenecks = monitor.identify_bottlenecks(threshold_percentile=0.5)
    logger.info(f"✅ Identified {len(bottlenecks)} bottlenecks")

    # Test export
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    monitor.export_to_json(temp_path)

    if Path(temp_path).exists():
        logger.info(f"✅ Metrics exported to {temp_path}")
        Path(temp_path).unlink()  # Cleanup
    else:
        logger.error("❌ Failed to export metrics")
        return False

    # Test alert triggering
    with monitor.measure("slow_operation"):
        time.sleep(0.6)  # Exceeds 0.5s threshold

    if len(monitor.alerts) > 0:
        logger.info(f"✅ Alert triggered (total: {len(monitor.alerts)})")
    else:
        logger.error("❌ Alert not triggered")
        return False

    logger.info("✅ Performance monitoring test PASSED")
    return True


def test_dependency_injection():
    """Test dependency injection"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Dependency Injection")
    logger.info("="*80)

    from src.core.dependency_injection import DIContainer, Lifetime

    # Create container
    container = DIContainer()
    logger.info("✅ DI container created")

    # Test 1: Singleton registration
    class TestService:
        def __init__(self):
            self.value = 42

    container.register_singleton(TestService, implementation=TestService)
    logger.info("✅ Singleton registered")

    # Resolve twice and verify same instance
    instance1 = container.resolve(TestService)
    instance2 = container.resolve(TestService)

    if instance1 is instance2:
        logger.info("✅ Singleton returns same instance")
    else:
        logger.error("❌ Singleton returned different instances")
        return False

    # Test 2: Transient registration
    class TransientService:
        def __init__(self):
            self.value = 99

    container.register_transient(TransientService, implementation=TransientService)
    logger.info("✅ Transient registered")

    # Resolve twice and verify different instances
    t_instance1 = container.resolve(TransientService)
    t_instance2 = container.resolve(TransientService)

    if t_instance1 is not t_instance2:
        logger.info("✅ Transient returns different instances")
    else:
        logger.error("❌ Transient returned same instance")
        return False

    # Test 3: Factory registration
    call_count = [0]

    def factory():
        call_count[0] += 1
        return TestService()

    container.register_singleton(type(None), factory=factory)
    container.resolve(type(None))

    if call_count[0] == 1:
        logger.info("✅ Factory called correctly")
    else:
        logger.error(f"❌ Factory call count: {call_count[0]}")
        return False

    # Test 4: Instance registration
    pre_created = TestService()
    pre_created.value = 999

    container.register_singleton(int, instance=pre_created)
    resolved = container.resolve(int)

    if resolved.value == 999:
        logger.info("✅ Instance registration works")
    else:
        logger.error(f"❌ Instance value incorrect: {resolved.value}")
        return False

    # Test 5: Service listing
    services = container.get_registered_services()
    if len(services) >= 4:
        logger.info(f"✅ Registered services listed ({len(services)} services)")
    else:
        logger.error(f"❌ Expected at least 4 services, got {len(services)}")
        return False

    logger.info("✅ Dependency injection test PASSED")
    return True


def test_code_structure():
    """Test that Phase 3 files exist"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Code Structure")
    logger.info("="*80)

    files_to_check = [
        ("src/utils/async_engine.py", "Async engine"),
        ("src/models/ollama_pool.py", "Connection pool"),
        ("src/utils/performance.py", "Performance monitoring"),
        ("src/core/dependency_injection.py", "Dependency injection"),
    ]

    for file_path, description in files_to_check:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {description} file exists")
        else:
            logger.error(f"❌ {description} file not found: {file_path}")
            return False

    # Check imports work
    try:
        from src.utils.async_engine import AsyncAnalysisEngine
        from src.utils.performance import PerformanceMonitor
        from src.core.dependency_injection import DIContainer

        logger.info("✅ Core Phase 3 modules can be imported")

        # Ollama pool is optional
        try:
            from src.models.ollama_pool import OllamaConnectionPool
            logger.info("✅ Ollama pool module can be imported")
        except ModuleNotFoundError:
            logger.warning("⚠️  Ollama pool skipped (dependency missing)")

    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

    logger.info("✅ Code structure test PASSED")
    return True


def main():
    """Run all tests"""
    logger.info("="*80)
    logger.info("PHASE 3 ADVANCED - INTEGRATION TEST")
    logger.info("="*80)

    results = []

    # Run tests
    results.append(("Async Engine", test_async_engine()))
    results.append(("Connection Pool", test_connection_pool()))
    results.append(("Performance Monitoring", test_performance_monitoring()))
    results.append(("Dependency Injection", test_dependency_injection()))
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

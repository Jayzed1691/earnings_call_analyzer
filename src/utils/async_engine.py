"""
Async/Parallel Analysis Engine

Provides concurrent analysis of transcript sections and speakers
for significant performance improvements on multi-section transcripts.
"""
import asyncio
import logging
from typing import Dict, List, Any, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class AnalysisTask:
    """Represents a single analysis task"""
    task_id: str
    analyzer_name: str
    text: str
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def duration(self) -> float:
        """Get task duration in seconds"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return 0.0


class AsyncAnalysisEngine:
    """
    Engine for running analyses concurrently

    Supports:
    - Async/await for I/O-bound operations (LLM calls)
    - Thread pools for CPU-bound operations
    - Process pools for heavy computation
    """

    def __init__(
        self,
        max_workers: int = 4,
        use_processes: bool = False
    ):
        """
        Initialize async analysis engine

        Args:
            max_workers: Maximum number of concurrent workers
            use_processes: Use process pool instead of thread pool
        """
        self.max_workers = max_workers
        self.use_processes = use_processes

        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
            logger.info(f"Initialized process pool with {max_workers} workers")
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            logger.info(f"Initialized thread pool with {max_workers} workers")

    async def analyze_sections_parallel(
        self,
        sections: Dict[str, str],
        analyzer_func: Callable[[str], T],
        analyzer_name: str = "analyzer"
    ) -> Dict[str, T]:
        """
        Analyze multiple sections in parallel

        Args:
            sections: Dictionary mapping section_name -> text
            analyzer_func: Function to analyze each section
            analyzer_name: Name of analyzer for logging

        Returns:
            Dictionary mapping section_name -> analysis result
        """
        if not sections:
            return {}

        logger.info(
            f"Starting parallel analysis of {len(sections)} sections "
            f"with {self.max_workers} workers"
        )

        # Create tasks for each section
        tasks = []
        task_metadata = []

        for section_name, text in sections.items():
            if not text or not text.strip():
                logger.debug(f"Skipping empty section: {section_name}")
                continue

            # Create async task
            task = asyncio.create_task(
                self._run_analysis_async(
                    section_name,
                    text,
                    analyzer_func,
                    analyzer_name
                )
            )
            tasks.append(task)
            task_metadata.append(section_name)

        # Run all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Process results
        section_results = {}
        for section_name, result in zip(task_metadata, results):
            if isinstance(result, Exception):
                logger.error(
                    f"Failed to analyze section '{section_name}': {result}"
                )
                raise result
            else:
                section_results[section_name] = result

        logger.info(
            f"Completed {len(section_results)} sections in {total_time:.2f}s "
            f"(avg: {total_time/len(section_results):.2f}s per section)"
        )

        return section_results

    async def analyze_speakers_parallel(
        self,
        speakers: Dict[str, str],
        analyzer_func: Callable[[str], T],
        analyzer_name: str = "analyzer"
    ) -> Dict[str, T]:
        """
        Analyze multiple speakers in parallel

        Args:
            speakers: Dictionary mapping speaker_name -> text
            analyzer_func: Function to analyze each speaker
            analyzer_name: Name of analyzer for logging

        Returns:
            Dictionary mapping speaker_name -> analysis result
        """
        return await self.analyze_sections_parallel(
            speakers,
            analyzer_func,
            analyzer_name
        )

    async def _run_analysis_async(
        self,
        identifier: str,
        text: str,
        analyzer_func: Callable[[str], T],
        analyzer_name: str
    ) -> T:
        """
        Run a single analysis task asynchronously

        Args:
            identifier: Section/speaker name
            text: Text to analyze
            analyzer_func: Analysis function
            analyzer_name: Analyzer name for logging

        Returns:
            Analysis result
        """
        logger.debug(f"Starting {analyzer_name} for '{identifier}'")
        start_time = time.time()

        # Run the blocking analyzer function in the executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            analyzer_func,
            text
        )

        duration = time.time() - start_time
        logger.debug(
            f"Completed {analyzer_name} for '{identifier}' in {duration:.2f}s"
        )

        return result

    async def run_multiple_analyzers(
        self,
        text: str,
        analyzers: Dict[str, Callable[[str], Any]]
    ) -> Dict[str, Any]:
        """
        Run multiple different analyzers on the same text concurrently

        Args:
            text: Text to analyze
            analyzers: Dictionary mapping analyzer_name -> analyzer_func

        Returns:
            Dictionary mapping analyzer_name -> result

        Example:
            results = await engine.run_multiple_analyzers(
                text,
                {
                    'sentiment': sentiment_analyzer.analyze,
                    'complexity': complexity_analyzer.analyze,
                    'numerical': numerical_analyzer.analyze
                }
            )
        """
        logger.info(f"Running {len(analyzers)} analyzers in parallel")

        tasks = []
        analyzer_names = []

        for name, analyzer_func in analyzers.items():
            task = asyncio.create_task(
                self._run_analysis_async(name, text, analyzer_func, name)
            )
            tasks.append(task)
            analyzer_names.append(name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        analyzer_results = {}
        for name, result in zip(analyzer_names, results):
            if isinstance(result, Exception):
                logger.error(f"Analyzer '{name}' failed: {result}")
                raise result
            else:
                analyzer_results[name] = result

        return analyzer_results

    def shutdown(self):
        """Shutdown the executor"""
        logger.info("Shutting down async analysis engine")
        self.executor.shutdown(wait=True)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
        return False


class ParallelBatchProcessor:
    """
    Batch processor for analyzing multiple transcripts in parallel

    Useful for processing large datasets
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize batch processor

        Args:
            max_workers: Maximum number of parallel transcripts to process
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_batch(
        self,
        transcripts: List[str],
        analyzer_func: Callable[[str], Any]
    ) -> List[Any]:
        """
        Process multiple transcripts in parallel

        Args:
            transcripts: List of transcript file paths
            analyzer_func: Function to analyze each transcript

        Returns:
            List of analysis results
        """
        logger.info(f"Processing batch of {len(transcripts)} transcripts")

        tasks = []
        for i, transcript_path in enumerate(transcripts):
            task = asyncio.create_task(
                self._process_single_transcript(
                    i,
                    transcript_path,
                    analyzer_func
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        successful_results = []
        failed_count = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Transcript {i} failed: {result}")
                failed_count += 1
            else:
                successful_results.append(result)

        logger.info(
            f"Batch complete: {len(successful_results)} succeeded, "
            f"{failed_count} failed"
        )

        return successful_results

    async def _process_single_transcript(
        self,
        index: int,
        transcript_path: str,
        analyzer_func: Callable[[str], Any]
    ) -> Any:
        """Process a single transcript"""
        logger.debug(f"Processing transcript {index}: {transcript_path}")
        start_time = time.time()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            analyzer_func,
            transcript_path
        )

        duration = time.time() - start_time
        logger.info(
            f"Transcript {index} completed in {duration:.2f}s"
        )

        return result

    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


# Utility function for easy async execution
def run_async(coro):
    """
    Run an async coroutine in a new event loop

    Useful for calling async code from sync context

    Args:
        coro: Coroutine to run

    Returns:
        Result of coroutine

    Example:
        result = run_async(engine.analyze_sections_parallel(...))
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, create new task
            return asyncio.create_task(coro)
    except RuntimeError:
        pass

    # Create new event loop
    return asyncio.run(coro)

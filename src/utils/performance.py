"""
Performance Monitoring and Metrics

Tracks performance metrics, identifies bottlenecks, and provides
insights into system performance.
"""
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from contextlib import contextmanager
import statistics
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    operation: str
    duration: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


@dataclass
class OperationStats:
    """Aggregated statistics for an operation"""
    operation: str
    count: int
    total_time: float
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    p95_time: float
    p99_time: float
    success_count: int
    failure_count: int
    success_rate: float


class PerformanceMonitor:
    """
    Monitor and track performance metrics

    Features:
    - Operation timing
    - Statistical aggregation
    - Bottleneck identification
    - Export to JSON/CSV
    - Real-time alerts
    """

    def __init__(
        self,
        enabled: bool = True,
        alert_threshold: float = 5.0,
        max_metrics: int = 10000
    ):
        """
        Initialize performance monitor

        Args:
            enabled: Whether monitoring is enabled
            alert_threshold: Alert if operation exceeds this time (seconds)
            max_metrics: Maximum metrics to store (prevents memory growth)
        """
        self.enabled = enabled
        self.alert_threshold = alert_threshold
        self.max_metrics = max_metrics

        # Storage
        self.metrics: List[PerformanceMetric] = []
        self.operation_metrics: Dict[str, List[float]] = defaultdict(list)

        # Alerts
        self.alerts: List[Dict[str, Any]] = []

        logger.info(
            f"Performance monitor initialized: "
            f"enabled={enabled}, alert_threshold={alert_threshold}s"
        )

    @contextmanager
    def measure(
        self,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Measure operation duration (context manager)

        Usage:
            with monitor.measure("llm_sentiment_analysis"):
                result = analyze_sentiment(text)

        Args:
            operation: Operation name
            metadata: Additional context
        """
        if not self.enabled:
            yield
            return

        start_time = time.time()
        success = True
        error = None

        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time

            # Record metric
            metric = PerformanceMetric(
                operation=operation,
                duration=duration,
                timestamp=start_time,
                metadata=metadata or {},
                success=success,
                error=error
            )

            self._record_metric(metric)

            # Check for alerts
            if duration > self.alert_threshold:
                self._trigger_alert(operation, duration, metadata)

    def _record_metric(self, metric: PerformanceMetric):
        """Record a metric"""
        # Add to list
        self.metrics.append(metric)
        self.operation_metrics[metric.operation].append(metric.duration)

        # Trim if exceeds max
        if len(self.metrics) > self.max_metrics:
            # Remove oldest 10%
            trim_count = self.max_metrics // 10
            self.metrics = self.metrics[trim_count:]
            logger.debug(f"Trimmed {trim_count} old metrics")

    def _trigger_alert(
        self,
        operation: str,
        duration: float,
        metadata: Optional[Dict[str, Any]]
    ):
        """Trigger performance alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'threshold': self.alert_threshold,
            'metadata': metadata
        }

        self.alerts.append(alert)

        logger.warning(
            f"PERFORMANCE ALERT: {operation} took {duration:.2f}s "
            f"(threshold: {self.alert_threshold}s)"
        )

    def get_stats(
        self,
        operation: Optional[str] = None
    ) -> Dict[str, OperationStats]:
        """
        Get performance statistics

        Args:
            operation: Get stats for specific operation (None = all)

        Returns:
            Dictionary mapping operation -> OperationStats
        """
        if operation:
            operations = [operation]
        else:
            operations = list(self.operation_metrics.keys())

        stats = {}

        for op in operations:
            durations = self.operation_metrics[op]
            if not durations:
                continue

            # Calculate statistics
            sorted_durations = sorted(durations)
            count = len(durations)

            # Success/failure counts
            success_count = sum(
                1 for m in self.metrics
                if m.operation == op and m.success
            )
            failure_count = count - success_count

            stats[op] = OperationStats(
                operation=op,
                count=count,
                total_time=sum(durations),
                min_time=min(durations),
                max_time=max(durations),
                avg_time=statistics.mean(durations),
                median_time=statistics.median(durations),
                p95_time=sorted_durations[int(count * 0.95)] if count > 0 else 0,
                p99_time=sorted_durations[int(count * 0.99)] if count > 0 else 0,
                success_count=success_count,
                failure_count=failure_count,
                success_rate=success_count / count if count > 0 else 0
            )

        return stats

    def identify_bottlenecks(
        self,
        threshold_percentile: float = 0.95
    ) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks

        Args:
            threshold_percentile: Operations above this percentile are bottlenecks

        Returns:
            List of bottleneck operations with details
        """
        stats = self.get_stats()

        if not stats:
            return []

        # Calculate overall time distribution
        all_avg_times = [s.avg_time for s in stats.values()]
        threshold = statistics.quantiles(all_avg_times, n=100)[int(threshold_percentile * 100) - 1]

        bottlenecks = []

        for op, stat in stats.items():
            if stat.avg_time >= threshold:
                bottleneck = {
                    'operation': op,
                    'avg_time': stat.avg_time,
                    'max_time': stat.max_time,
                    'count': stat.count,
                    'total_time': stat.total_time,
                    'percentage_of_total': 0.0  # Will calculate below
                }
                bottlenecks.append(bottleneck)

        # Calculate percentage of total time
        total_time = sum(b['total_time'] for b in bottlenecks)
        for b in bottlenecks:
            b['percentage_of_total'] = (b['total_time'] / total_time * 100) if total_time > 0 else 0

        # Sort by total time (highest impact first)
        bottlenecks.sort(key=lambda x: x['total_time'], reverse=True)

        return bottlenecks

    def export_to_json(self, file_path: str):
        """
        Export metrics to JSON file

        Args:
            file_path: Output file path
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_metrics': len(self.metrics),
            'stats': {
                op: asdict(stat)
                for op, stat in self.get_stats().items()
            },
            'bottlenecks': self.identify_bottlenecks(),
            'alerts': self.alerts,
            'recent_metrics': [
                asdict(m) for m in self.metrics[-100:]  # Last 100 metrics
            ]
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Exported performance metrics to {file_path}")

    def print_summary(self):
        """Print performance summary to console"""
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)

        stats = self.get_stats()

        if not stats:
            print("No metrics recorded")
            return

        # Overall stats
        total_operations = sum(s.count for s in stats.values())
        total_time = sum(s.total_time for s in stats.values())
        total_failures = sum(s.failure_count for s in stats.values())

        print(f"\nOverall Statistics:")
        print(f"  Total Operations: {total_operations}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Total Failures: {total_failures}")
        print(f"  Success Rate: {((total_operations - total_failures) / total_operations * 100):.1f}%")

        # Top operations by time
        print(f"\nTop Operations by Total Time:")
        sorted_ops = sorted(
            stats.items(),
            key=lambda x: x[1].total_time,
            reverse=True
        )

        for i, (op, stat) in enumerate(sorted_ops[:10], 1):
            pct = (stat.total_time / total_time * 100) if total_time > 0 else 0
            print(
                f"  {i}. {op}: {stat.total_time:.2f}s "
                f"({pct:.1f}%, {stat.count} calls, "
                f"avg: {stat.avg_time:.2f}s)"
            )

        # Bottlenecks
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks:
            print(f"\nIdentified Bottlenecks:")
            for i, b in enumerate(bottlenecks[:5], 1):
                print(
                    f"  {i}. {b['operation']}: avg {b['avg_time']:.2f}s, "
                    f"max {b['max_time']:.2f}s ({b['count']} calls)"
                )

        # Alerts
        if self.alerts:
            print(f"\nPerformance Alerts: {len(self.alerts)}")
            for alert in self.alerts[-5:]:  # Last 5
                print(
                    f"  • {alert['operation']}: {alert['duration']:.2f}s "
                    f"at {alert['timestamp']}"
                )

        print("="*80 + "\n")

    def clear(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.operation_metrics.clear()
        self.alerts.clear()
        logger.info("Cleared all performance metrics")

    def get_slowest_operations(self, n: int = 10) -> List[PerformanceMetric]:
        """
        Get the N slowest individual operations

        Args:
            n: Number of operations to return

        Returns:
            List of slowest PerformanceMetric objects
        """
        sorted_metrics = sorted(
            self.metrics,
            key=lambda m: m.duration,
            reverse=True
        )
        return sorted_metrics[:n]


# Global performance monitor
_global_monitor: Optional[PerformanceMonitor] = None


def get_monitor(
    enabled: Optional[bool] = None,
    alert_threshold: Optional[float] = None
) -> PerformanceMonitor:
    """
    Get or create global performance monitor

    Args:
        enabled: Enable monitoring (default: from settings or True)
        alert_threshold: Alert threshold in seconds (default: 5.0)

    Returns:
        Global PerformanceMonitor instance
    """
    global _global_monitor

    if _global_monitor is None:
        from config.settings import settings

        enabled = enabled if enabled is not None else getattr(
            settings,
            'ENABLE_PERFORMANCE_MONITORING',
            True
        )

        alert_threshold = alert_threshold or getattr(
            settings,
            'PERFORMANCE_ALERT_THRESHOLD',
            5.0
        )

        _global_monitor = PerformanceMonitor(
            enabled=enabled,
            alert_threshold=alert_threshold
        )

    return _global_monitor


def reset_monitor():
    """Reset global monitor (useful for testing)"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.clear()
        _global_monitor = None

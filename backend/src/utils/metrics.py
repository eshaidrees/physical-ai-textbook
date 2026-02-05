from typing import Dict, Any, Optional
from datetime import datetime
import time
import threading
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
from collections import defaultdict, deque
from ..utils.logging import app_logger


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """
    Represents a single metric with its metadata
    """
    name: str
    value: float
    type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    description: Optional[str] = None


class MetricsCollector:
    """
    Collects and manages application metrics
    """
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.histograms: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'values': [],
            'count': 0,
            'sum': 0.0,
            'labels': {}
        })
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.request_times = deque(maxlen=1000)  # Keep last 1000 request times
        self.error_counts = defaultdict(int)
        self.conversation_counts = defaultdict(int)

    def increment_counter(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric
        """
        labels = labels or {}
        key = f"{name}_{hash(frozenset(labels.items()))}"

        with self.lock:
            self.counters[key] += amount

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric to a specific value
        """
        labels = labels or {}
        key = f"{name}_{hash(frozenset(labels.items()))}"

        with self.lock:
            self.gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Observe a value for a histogram metric
        """
        labels = labels or {}
        key = f"{name}_{hash(frozenset(labels.items()))}"

        with self.lock:
            self.histograms[key]['values'].append(value)
            self.histograms[key]['count'] += 1
            self.histograms[key]['sum'] += value
            if not self.histograms[key]['labels']:  # Only set labels on first observation
                self.histograms[key]['labels'] = labels

    def record_request_time(self, duration: float, endpoint: str = "unknown"):
        """
        Record the time taken for a request
        """
        with self.lock:
            self.request_times.append({
                'duration': duration,
                'endpoint': endpoint,
                'timestamp': datetime.now()
            })

    def increment_error_count(self, error_type: str = "generic"):
        """
        Increment the count of a specific error type
        """
        with self.lock:
            self.error_counts[error_type] += 1

    def increment_conversation_count(self, conversation_type: str = "generic"):
        """
        Increment the count of a specific conversation type
        """
        with self.lock:
            self.conversation_counts[conversation_type] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics
        """
        with self.lock:
            metrics = {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': dict(self.histograms),
                'request_times': list(self.request_times)[-100:],  # Last 100 requests
                'error_counts': dict(self.error_counts),
                'conversation_counts': dict(self.conversation_counts),
                'timestamp': datetime.now().isoformat()
            }
            return metrics

    def get_average_response_time(self) -> float:
        """
        Calculate the average response time
        """
        with self.lock:
            if not self.request_times:
                return 0.0
            total_time = sum(req['duration'] for req in self.request_times)
            return total_time / len(self.request_times)

    def get_p95_response_time(self) -> float:
        """
        Calculate the 95th percentile response time
        """
        with self.lock:
            if not self.request_times:
                return 0.0

            sorted_times = sorted([req['duration'] for req in self.request_times])
            index = int(0.95 * len(sorted_times))
            if index >= len(sorted_times):
                index = len(sorted_times) - 1

            return sorted_times[index]

    def get_error_rate(self) -> float:
        """
        Calculate the error rate
        """
        with self.lock:
            total_requests = len(self.request_times)
            if total_requests == 0:
                return 0.0

            total_errors = sum(self.error_counts.values())
            return total_errors / total_requests

    def reset(self):
        """
        Reset all metrics
        """
        with self.lock:
            self.metrics.clear()
            self.histograms.clear()
            self.counters.clear()
            self.gauges.clear()
            self.request_times.clear()
            self.error_counts.clear()
            self.conversation_counts.clear()


class PerformanceMonitor:
    """
    Monitors and logs performance metrics
    """
    def __init__(self):
        self.collector = MetricsCollector()
        self.start_time = time.time()

    def measure_endpoint_performance(self, endpoint: str):
        """
        Decorator to measure the performance of an endpoint
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start_time
                    self.collector.record_request_time(duration, endpoint)
                    app_logger.info(
                        f"Endpoint {endpoint} completed in {duration:.4f}s",
                        extra={'duration': duration, 'endpoint': endpoint}
                    )
                    return result
                except Exception as e:
                    duration = time.perf_counter() - start_time
                    self.collector.record_request_time(duration, endpoint)
                    self.collector.increment_error_count(type(e).__name__)
                    app_logger.error(
                        f"Endpoint {endpoint} failed after {duration:.4f}s: {str(e)}",
                        extra={'duration': duration, 'endpoint': endpoint, 'error': str(e)}
                    )
                    raise
            return wrapper
        return decorator

    def measure_function_performance(self, name: str):
        """
        Decorator to measure the performance of any function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start_time
                    self.collector.observe_histogram(f"function_duration_{name}", duration)
                    app_logger.debug(
                        f"Function {name} completed in {duration:.4f}s",
                        extra={'function': name, 'duration': duration}
                    )
                    return result
                except Exception as e:
                    duration = time.perf_counter() - start_time
                    self.collector.observe_histogram(f"function_duration_{name}", duration)
                    app_logger.error(
                        f"Function {name} failed after {duration:.4f}s: {str(e)}",
                        extra={'function': name, 'duration': duration, 'error': str(e)}
                    )
                    raise
            return wrapper
        return decorator

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system-level metrics
        """
        import psutil
        import os

        process = psutil.Process(os.getpid())

        return {
            'uptime': time.time() - self.start_time,
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'cpu_percent': process.cpu_percent(),
            'num_threads': process.num_threads(),
            'num_fds': process.num_fds() if os.name != 'nt' else 'N/A',  # Not available on Windows
            'timestamp': datetime.now().isoformat()
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance report
        """
        metrics = self.collector.get_metrics()
        system_metrics = self.get_system_metrics()

        report = {
            'system_metrics': system_metrics,
            'application_metrics': metrics,
            'calculated_metrics': {
                'average_response_time': self.collector.get_average_response_time(),
                'p95_response_time': self.collector.get_p95_response_time(),
                'error_rate': self.collector.get_error_rate(),
                'requests_per_minute': len(metrics['request_times']) / (system_metrics['uptime'] / 60) if system_metrics['uptime'] > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        }

        return report

    def log_performance_report(self):
        """
        Log the current performance report
        """
        report = self.get_performance_report()
        app_logger.info("Performance Report", extra=report)

    def save_metrics_to_file(self, filepath: str):
        """
        Save current metrics to a JSON file
        """
        report = self.get_performance_report()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance
    """
    return performance_monitor


def monitor_performance():
    """
    Context manager for monitoring performance of a code block
    """
    start_time = time.perf_counter()

    class Monitor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.perf_counter() - start_time
            if exc_type is None:
                app_logger.info(f"Operation completed in {duration:.4f}s", extra={'duration': duration})
            else:
                app_logger.error(f"Operation failed after {duration:.4f}s", extra={'duration': duration, 'error': str(exc_val)})

    return Monitor()


# Initialize metrics
app_logger.info("Performance monitoring initialized")
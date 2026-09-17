"""
B-SDD Production Telemetry & Observability Adapter (ADR-012).
Collects high-precision latency quantiles, compiler SLA compliance,
HTTP throughput, cache hit ratios, and Prometheus text metrics.
100% Pure Python Standard Library.
"""
import os
import sys
import time
import math
import json
import resource
import threading
from collections import deque, defaultdict
from contextlib import contextmanager
from typing import Dict, Any, List, Optional, Tuple


class SlidingWindowQuantiles:
    """Thread-safe ring buffer for streaming latency quantile computation."""

    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self._samples = deque(maxlen=max_samples)
        self._lock = threading.Lock()

    def record(self, value: float) -> None:
        with self._lock:
            self._samples.append(value)

    def get_stats(self) -> Dict[str, float]:
        with self._lock:
            if not self._samples:
                return {
                    "count": 0,
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0,
                    "p50": 0.0,
                    "p90": 0.0,
                    "p95": 0.0,
                    "p99": 0.0,
                }
            sorted_vals = sorted(self._samples)
            n = len(sorted_vals)

            def quantile(q: float) -> float:
                idx = int(math.ceil(q * n)) - 1
                return sorted_vals[max(0, min(idx, n - 1))]

            return {
                "count": n,
                "min": round(sorted_vals[0], 2),
                "max": round(sorted_vals[-1], 2),
                "avg": round(sum(sorted_vals) / n, 2),
                "p50": round(quantile(0.50), 2),
                "p90": round(quantile(0.90), 2),
                "p95": round(quantile(0.95), 2),
                "p99": round(quantile(0.99), 2),
            }

    def clear(self) -> None:
        with self._lock:
            self._samples.clear()


class TelemetryCollector:
    """
    Central sovereign telemetry and metrics aggregator for B-SDD.
    Tracks compiler SLA (<50ms), HTTP latencies, cache ratios, and active clients.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._start_time = time.time()

        # Compiler metrics
        self.compile_latencies = SlidingWindowQuantiles(max_samples=500)
        self.last_compile_ms: float = 0.0
        self.total_compiles: int = 0
        self.failed_compiles: int = 0
        self.last_word_count: int = 0
        self.word_budget: int = 500
        self.sla_violations: int = 0  # Compiles exceeding 50ms

        # HTTP metrics
        self.request_latencies = SlidingWindowQuantiles(max_samples=1000)
        self.total_requests: int = 0
        self.requests_by_endpoint: Dict[str, int] = defaultdict(int)
        self.requests_by_status: Dict[int, int] = defaultdict(int)

        # DRAKON validation metrics
        self.drakon_latencies = SlidingWindowQuantiles(max_samples=500)
        self.drakon_validations_total: int = 0
        self.drakon_invalid_count: int = 0

        # Cache metrics
        self.cache_hits: Dict[str, int] = defaultdict(int)
        self.cache_misses: Dict[str, int] = defaultdict(int)

        # Realtime SSE metrics
        self.active_sse_connections: int = 0
        self.sse_events_broadcast: int = 0

        # Invariant verification metrics
        self.invariant_checks_total: int = 0
        self.invariant_violations: int = 0

    def reset(self) -> None:
        """Resets all metrics (primarily used in automated test isolation)."""
        with self._lock:
            self._start_time = time.time()
            self.compile_latencies.clear()
            self.request_latencies.clear()
            self.drakon_latencies.clear()
            self.last_compile_ms = 0.0
            self.total_compiles = 0
            self.failed_compiles = 0
            self.last_word_count = 0
            self.sla_violations = 0
            self.total_requests = 0
            self.requests_by_endpoint.clear()
            self.requests_by_status.clear()
            self.drakon_validations_total = 0
            self.drakon_invalid_count = 0
            self.cache_hits.clear()
            self.cache_misses.clear()
            self.active_sse_connections = 0
            self.sse_events_broadcast = 0
            self.invariant_checks_total = 0
            self.invariant_violations = 0

    @contextmanager
    def measure_latency(self, metric_name: str, **kwargs):
        """Zero-overhead context manager to measure and record execution time."""
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            if metric_name == "compile":
                self.record_compile(
                    duration_ms=elapsed_ms,
                    word_count=kwargs.get("word_count", self.last_word_count),
                    success=kwargs.get("success", True),
                )
            elif metric_name == "request":
                self.record_request(
                    method=kwargs.get("method", "GET"),
                    path=kwargs.get("path", "/"),
                    status=kwargs.get("status", 200),
                    duration_ms=elapsed_ms,
                )
            elif metric_name == "drakon":
                self.record_drakon_validation(
                    duration_ms=elapsed_ms,
                    is_valid=kwargs.get("is_valid", True),
                )

    def record_compile(
        self, duration_ms: float, word_count: int, success: bool = True, budget: int = 500
    ) -> None:
        """Records active rules compilation outcome and evaluates SLA."""
        with self._lock:
            self.total_compiles += 1
            if not success:
                self.failed_compiles += 1
            self.last_compile_ms = round(duration_ms, 2)
            self.last_word_count = word_count
            self.word_budget = budget
            if duration_ms > 50.0:
                self.sla_violations += 1
        self.compile_latencies.record(duration_ms)

    def record_request(
        self, method: str, path: str, status: int, duration_ms: float
    ) -> None:
        """Records incoming HTTP request duration and status code."""
        with self._lock:
            self.total_requests += 1
            key = f"{method.upper()} {path.split('?')[0].rstrip('/')}"
            self.requests_by_endpoint[key] += 1
            self.requests_by_status[status] += 1
        self.request_latencies.record(duration_ms)

    def record_drakon_validation(self, duration_ms: float, is_valid: bool = True) -> None:
        """Records DRAKON visual logic planarity and constraint validation."""
        with self._lock:
            self.drakon_validations_total += 1
            if not is_valid:
                self.drakon_invalid_count += 1
        self.drakon_latencies.record(duration_ms)

    def record_cache_access(self, cache_name: str, hit: bool) -> None:
        """Records hit or miss for specified cache (e.g. 'github', 'utopia')."""
        with self._lock:
            if hit:
                self.cache_hits[cache_name] += 1
            else:
                self.cache_misses[cache_name] += 1

    def record_sse_connect(self) -> None:
        """Increments active SSE connections gauge."""
        with self._lock:
            self.active_sse_connections += 1

    def record_sse_disconnect(self) -> None:
        """Decrements active SSE connections gauge."""
        with self._lock:
            self.active_sse_connections = max(0, self.active_sse_connections - 1)

    def record_sse_broadcast(self) -> None:
        """Increments broadcast event counter."""
        with self._lock:
            self.sse_events_broadcast += 1

    def record_invariant_check(self, passed: bool) -> None:
        """Records invariant assertion result."""
        with self._lock:
            self.invariant_checks_total += 1
            if not passed:
                self.invariant_violations += 1

    def get_memory_rss_mb(self) -> float:
        """Extracts current process RSS in MB via standard library resource module."""
        try:
            rusage = resource.getrusage(resource.RUSAGE_SELF)
            # Linux reports in kilobytes, macOS in bytes
            multiplier = 1024.0 if sys.platform != "darwin" else (1024.0 * 1024.0)
            return round(rusage.ru_maxrss / multiplier, 2)
        except Exception:
            return 0.0

    def get_summary(self) -> Dict[str, Any]:
        """Returns structured JSON summary of all telemetry metrics."""
        now = time.time()
        uptime = round(now - self._start_time, 2)
        rps = round(self.total_requests / max(1.0, uptime), 2)

        with self._lock:
            comp_stats = self.compile_latencies.get_stats()
            req_stats = self.request_latencies.get_stats()
            drakon_stats = self.drakon_latencies.get_stats()

            gh_hits = self.cache_hits.get("github", 0)
            gh_miss = self.cache_misses.get("github", 0)
            gh_total = gh_hits + gh_miss
            gh_ratio = round(gh_hits / gh_total, 2) if gh_total > 0 else 1.0

            utopia_hits = self.cache_hits.get("utopia", 0)
            utopia_miss = self.cache_misses.get("utopia", 0)
            utopia_total = utopia_hits + utopia_miss
            utopia_ratio = round(utopia_hits / utopia_total, 2) if utopia_total > 0 else 1.0

            status_code_dict = {str(k): v for k, v in sorted(self.requests_by_status.items())}
            endpoint_dict = dict(sorted(self.requests_by_endpoint.items(), key=lambda x: -x[1])[:10])

            # Determine overall health status
            sla_ok = self.last_compile_ms <= 50.0 and self.sla_violations == 0
            err_count = sum(v for k, v in self.requests_by_status.items() if k >= 500)
            overall_status = "healthy"
            if not sla_ok or err_count > 0 or self.invariant_violations > 0:
                overall_status = "degraded"

            summary = {
                "status": overall_status,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                "uptime_seconds": uptime,
                "memory_rss_mb": self.get_memory_rss_mb(),
                "compiler": {
                    "last_compile_ms": self.last_compile_ms,
                    "compile_count": self.total_compiles,
                    "failed_compiles": self.failed_compiles,
                    "word_count": self.last_word_count,
                    "max_budget": self.word_budget,
                    "sla_target_ms": 50.0,
                    "sla_passed": self.last_compile_ms <= 50.0,
                    "sla_violations": self.sla_violations,
                    "quantiles": comp_stats,
                },
                "http": {
                    "total_requests": self.total_requests,
                    "requests_per_sec": rps,
                    "status_codes": status_code_dict,
                    "top_endpoints": endpoint_dict,
                    "active_sse_connections": self.active_sse_connections,
                    "sse_events_broadcast": self.sse_events_broadcast,
                    "quantiles": req_stats,
                },
                "drakon": {
                    "validations_total": self.drakon_validations_total,
                    "invalid_count": self.drakon_invalid_count,
                    "quantiles": drakon_stats,
                },
                "cache": {
                    "github": {
                        "hits": gh_hits,
                        "misses": gh_miss,
                        "hit_ratio": gh_ratio,
                    },
                    "utopia": {
                        "hits": utopia_hits,
                        "misses": utopia_miss,
                        "hit_ratio": utopia_ratio,
                    },
                },
                "invariants": {
                    "checks_total": self.invariant_checks_total,
                    "violations": self.invariant_violations,
                },
                "deployment": {
                    "environment": os.environ.get("BSDD_ENV", "production"),
                    "cf_pages_url": "https://b-sdd-ui.pages.dev",
                    "gateway_url": "https://bsdd.exodus.pp.ua",
                    "systemd_service": "b-sdd-workbench.service",
                    "systemd_status": "running" if os.environ.get("INVOCATION_ID") else "unknown",
                },
            }
            return summary

    def get_prometheus_metrics(self) -> str:
        """Renders metrics in standard Prometheus text exposition format (ADR-012)."""
        summary = self.get_summary()
        c_quant = summary["compiler"]["quantiles"]
        h_quant = summary["http"]["quantiles"]

        lines = [
            "# HELP bsdd_compile_latency_ms Active rules compilation latency in milliseconds",
            "# TYPE bsdd_compile_latency_ms summary",
            f'bsdd_compile_latency_ms{{quantile="0.5"}} {c_quant["p50"]}',
            f'bsdd_compile_latency_ms{{quantile="0.9"}} {c_quant["p90"]}',
            f'bsdd_compile_latency_ms{{quantile="0.95"}} {c_quant["p95"]}',
            f'bsdd_compile_latency_ms{{quantile="0.99"}} {c_quant["p99"]}',
            f'bsdd_compile_latency_ms_sum {round(c_quant["avg"] * c_quant["count"], 2)}',
            f'bsdd_compile_latency_ms_count {c_quant["count"]}',
            "",
            "# HELP bsdd_compile_last_ms Last compilation execution duration in milliseconds",
            "# TYPE bsdd_compile_last_ms gauge",
            f'bsdd_compile_last_ms {summary["compiler"]["last_compile_ms"]}',
            "",
            "# HELP bsdd_compile_word_count Number of words in compiled active rules snapshot",
            "# TYPE bsdd_compile_word_count gauge",
            f'bsdd_compile_word_count {summary["compiler"]["word_count"]}',
            "",
            "# HELP bsdd_compile_sla_violations_total Compilations exceeding sub-50ms SLA budget",
            "# TYPE bsdd_compile_sla_violations_total counter",
            f'bsdd_compile_sla_violations_total {summary["compiler"]["sla_violations"]}',
            "",
            "# HELP bsdd_http_requests_total Total number of HTTP requests processed",
            "# TYPE bsdd_http_requests_total counter",
            f'bsdd_http_requests_total {summary["http"]["total_requests"]}',
            "",
            "# HELP bsdd_http_latency_ms HTTP request latency in milliseconds",
            "# TYPE bsdd_http_latency_ms summary",
            f'bsdd_http_latency_ms{{quantile="0.5"}} {h_quant["p50"]}',
            f'bsdd_http_latency_ms{{quantile="0.95"}} {h_quant["p95"]}',
            f'bsdd_http_latency_ms{{quantile="0.99"}} {h_quant["p99"]}',
            f'bsdd_http_latency_ms_sum {round(h_quant["avg"] * h_quant["count"], 2)}',
            f'bsdd_http_latency_ms_count {h_quant["count"]}',
            "",
            "# HELP bsdd_active_sse_connections Current count of active SSE client streams",
            "# TYPE bsdd_active_sse_connections gauge",
            f'bsdd_active_sse_connections {summary["http"]["active_sse_connections"]}',
            "",
            "# HELP bsdd_cache_hit_ratio Cache hit ratio by backend",
            "# TYPE bsdd_cache_hit_ratio gauge",
            f'bsdd_cache_hit_ratio{{backend="github"}} {summary["cache"]["github"]["hit_ratio"]}',
            f'bsdd_cache_hit_ratio{{backend="utopia"}} {summary["cache"]["utopia"]["hit_ratio"]}',
            "",
            "# HELP bsdd_memory_rss_mb Resident memory set size in megabytes",
            "# TYPE bsdd_memory_rss_mb gauge",
            f'bsdd_memory_rss_mb {summary["memory_rss_mb"]}',
            "",
            "# HELP bsdd_uptime_seconds Workbench process uptime in seconds",
            "# TYPE bsdd_uptime_seconds counter",
            f'bsdd_uptime_seconds {summary["uptime_seconds"]}',
            "",
            "# HELP bsdd_invariant_violations_total Total detected architectural invariant violations",
            "# TYPE bsdd_invariant_violations_total counter",
            f'bsdd_invariant_violations_total {summary["invariants"]["violations"]}',
        ]
        return "\n".join(lines) + "\n"


# Global singleton instance
TELEMETRY = TelemetryCollector()

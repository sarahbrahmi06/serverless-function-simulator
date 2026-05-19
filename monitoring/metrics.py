import threading
import statistics
from typing import Dict, List, Any
from collections import defaultdict

class MetricsCollector:
    """Aggregates execution metrics across all function invocations."""
    def __init__(self):
        self._data: Dict[str, List[Dict]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, function_name: str, metrics: Dict[str, Any]):
        with self._lock:
            self._data[function_name].append(metrics)

    def summary(self, function_name: str) -> Dict[str, Any]:
        with self._lock:
            records = self._data.get(function_name, [])
            if not records: return {}
            
            durations = [r["duration_ms"] for r in records]
            memories = [r["memory_used_mb"] for r in records]
            cold_starts = sum(1 for r in records if r.get("cold_start_overhead_ms", 0) > 0)
            
            return {
                "function": function_name,
                "invocations": len(records),
                "cold_starts": cold_starts,
                "latency_avg_ms": round(statistics.mean(durations), 2) if durations else 0,
                "latency_p50_ms": round(statistics.median(durations), 2) if durations else 0,
                "latency_p95_ms": round(statistics.quantiles(durations, n=20)[18], 2) if len(durations) >= 2 else round(statistics.mean(durations), 2) if durations else 0,
                "memory_avg_mb": round(statistics.mean(memories), 2) if memories else 0,
                "memory_peak_mb": round(max([r["memory_peak_mb"] for r in records]), 2) if records else 0
            }
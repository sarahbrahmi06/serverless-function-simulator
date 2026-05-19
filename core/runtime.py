import asyncio
import time
import traceback
import psutil
import os
from typing import Callable, Any, Dict, Optional
from core.context import FunctionContext
from monitoring.logger import FunctionLogger
from monitoring.metrics import MetricsCollector

class FunctionRuntime:
    _warm_pool: Dict[str, Callable] = {}
    _cold_start_overhead_ms: int = 350

    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
        self.process = psutil.Process(os.getpid())

    async def invoke(self, handler: Callable, event: Dict[str, Any], context: FunctionContext) -> Dict[str, Any]:
        fn_name = context.function_name
        invocation_id = context.invocation_id
        cold_start = fn_name not in self._warm_pool
        
        FunctionLogger.info(invocation_id, fn_name, f"INIT | cold_start={cold_start}")

        if cold_start:
            await asyncio.sleep(self._cold_start_overhead_ms / 1000.0)
            self._warm_pool[fn_name] = handler
            FunctionLogger.info(invocation_id, fn_name, f"COLD_START complete | delay={self._cold_start_overhead_ms}ms")

        mem_before = self.process.memory_info().rss / (1024 * 1024)
        start_ts = time.perf_counter()
        
        result_envelope = {
            "invocation_id": invocation_id,
            "function": fn_name,
            "cold_start": cold_start,
            "status": "success",
            "result": None,
            "error": None,
            "metrics": {}
        }

        try:
            result = await asyncio.wait_for(
                self._run_handler(handler, event, context),
                timeout=context.timeout_seconds
            )
            result_envelope["result"] = result
            FunctionLogger.info(invocation_id, fn_name, "EXECUTION complete")
        except asyncio.TimeoutError:
            result_envelope["status"] = "timeout"
            result_envelope["error"] = f"Function exceeded timeout of {context.timeout_seconds}s"
            FunctionLogger.error(invocation_id, fn_name, result_envelope["error"])
        except Exception as exc:
            result_envelope["status"] = "error"
            result_envelope["error"] = str(exc)
            result_envelope["traceback"] = traceback.format_exc()
            FunctionLogger.error(invocation_id, fn_name, f"EXCEPTION: {exc}")
        finally:
            duration_ms = (time.perf_counter() - start_ts) * 1000
            mem_after = self.process.memory_info().rss / (1024 * 1024)
            
            result_envelope["metrics"] = {
                "duration_ms": round(duration_ms, 2),
                "memory_used_mb": round(max(0, mem_after - mem_before), 2),
                "memory_peak_mb": round(mem_after, 2),
                "cold_start_overhead_ms": self._cold_start_overhead_ms if cold_start else 0,
                "billed_duration_ms": self._calc_billed(duration_ms),
            }
            self.metrics.record(fn_name, result_envelope["metrics"])

        return result_envelope

    @staticmethod
    def _calc_billed(duration_ms: float) -> int:
        return max(1, int(duration_ms))

    @staticmethod
    async def _run_handler(handler: Callable, event: Dict, context: FunctionContext) -> Any:
        if asyncio.iscoroutinefunction(handler):
            return await handler(event, context)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, handler, event, context)
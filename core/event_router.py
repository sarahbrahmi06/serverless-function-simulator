import asyncio
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from core.context import FunctionContext
from core.runtime import FunctionRuntime

@dataclass
class TriggerRule:
    trigger_type: str  # "http", "timer", "queue"
    function_name: str
    handler: Callable
    config: Dict[str, Any] = field(default_factory=dict)
    memory_mb: int = 128
    timeout_s: int = 30
    version: str = "$LATEST"

class EventRouter:
    def __init__(self, runtime: FunctionRuntime):
        self.runtime = runtime
        self._registry: Dict[str, List[TriggerRule]] = {}

    def register(self, rule: TriggerRule):
        self._registry.setdefault(rule.trigger_type, []).append(rule)
        print(f"[Router] Registered trigger rule: {rule.trigger_type} -> {rule.function_name}")

    async def dispatch(self, trigger_type: str, event: Dict[str, Any], target_function: Optional[str] = None) -> List[Dict]:
        handlers = self._registry.get(trigger_type, [])
        if target_function:
            handlers = [h for h in handlers if h.function_name == target_function]

        if not handlers:
            return [{"error": f"No handler registered for trigger '{trigger_type}'"}]

        tasks = []
        for rule in handlers:
            ctx = FunctionContext(
                function_name=rule.function_name,
                function_version=rule.version,
                memory_limit_mb=rule.memory_mb,
                timeout_seconds=rule.timeout_s
            )
            tasks.append(self.runtime.invoke(rule.handler, event, ctx))
        
        return await asyncio.gather(*tasks)
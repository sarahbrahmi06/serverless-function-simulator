import uuid
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class FunctionContext:
    function_name: str
    function_version: str = "$LATEST"
    invocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_limit_mb: int = 128
    timeout_seconds: int = 30
    region: str = "us-east-1"
    _start_time: float = field(default_factory=time.time, repr=False)
    _env_vars: Dict[str, str] = field(default_factory=dict, repr=False)

    def get_remaining_time_ms(self) -> int:
        """Returns milliseconds left before timeout."""
        elapsed = (time.time() - self._start_time) * 1000
        remaining = (self.timeout_seconds * 1000) - elapsed
        return max(0, int(remaining))

    def log(self, message: str, level: str = "INFO"):
        """Structured contextual logging."""
        from monitoring.logger import FunctionLogger
        FunctionLogger.log(
            invocation_id=self.invocation_id,
            function=self.function_name,
            level=level,
            message=message
        )

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._env_vars.get(key, default)
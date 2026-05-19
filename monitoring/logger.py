import json
import time
import threading
from typing import List, Dict, Any
from datetime import datetime, timezone

class FunctionLogger:
    """Thread-safe structured logger for serverless function invocations."""
    _logs: List[Dict[str, Any]] = []
    _lock = threading.Lock()
    _log_file: str = "function_execution.log"

    @classmethod
    def _write(cls, level: str, invocation_id: str, function: str, message: str):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch_ms": int(time.time() * 1000),
            "level": level,
            "invocation_id": invocation_id,
            "function": function,
            "message": message,
        }
        with cls._lock:
            cls._logs.append(entry)
            with open(cls._log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        
        color = {
            "INFO": "\033[36m", "WARN": "\033[33m",
            "ERROR": "\033[31m", "DEBUG": "\033[35m"
        }.get(level, "\033[0m")
        
        print(f"{color}[{level}]\033[0m "
              f"\033[90m{entry['timestamp']}\033[0m "
              f"\033[32m{function}\033[0m "
              f"\033[90m({invocation_id[:8]}...)\033[0m "
              f"{message}")

    @classmethod
    def info(cls, inv_id, fn, msg): cls._write("INFO", inv_id, fn, msg)
    @classmethod
    def warn(cls, inv_id, fn, msg): cls._write("WARN", inv_id, fn, msg)
    @classmethod
    def error(cls, inv_id, fn, msg): cls._write("ERROR", inv_id, fn, msg)
    @classmethod
    def log(cls, invocation_id, function, level, message):
        cls._write(level, invocation_id, function, message)

    @classmethod
    def get_logs(cls, function: str = None, level: str = None) -> List[Dict]:
        with cls._lock:
            logs = cls._logs.copy()
            if function: logs = [l for l in logs if l["function"] == function]
            if level: logs = [l for l in logs if l["level"] == level]
            return logs

    @classmethod
    def clear(cls):
        with cls._lock: cls._logs.clear()
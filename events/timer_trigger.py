import schedule
import asyncio
import threading
import time
from typing import Dict, Any
from core.event_router import EventRouter

class TimerTrigger:
    def __init__(self, router: EventRouter):
        self.router = router
        self._scheduler_thread = None
        self._running = False

    def register(self, function_name: str, interval_seconds: int, payload: Dict[str, Any] = None):
        event = {
            "trigger": "timer",
            "interval": f"{interval_seconds}s",
            "body": payload or {}
        }
        schedule.every(interval_seconds).seconds.do(self._fire, function_name, event)
        print(f"[Timer] Scheduled periodic trigger cron loop for '{function_name}' every {interval_seconds}s")

    def _fire(self, function_name: str, event: Dict):
        asyncio.run(self.router.dispatch("timer", event, function_name))

    def start(self):
        self._running = True
        def run():
            while self._running:
                schedule.run_pending()
                time.sleep(0.5)
        self._scheduler_thread = threading.Thread(target=run, daemon=True)
        self._scheduler_thread.start()
        print("[Timer] Background daemon cron threads active")

    def stop(self):
        self._running = False
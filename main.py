import asyncio
import uvicorn
from core.runtime import FunctionRuntime
from core.event_router import EventRouter, TriggerRule
from monitoring.metrics import MetricsCollector
from events.http_trigger import create_http_gateway
from events.timer_trigger import TimerTrigger

# Import handoff reference points
import functions.process_order
import functions.resize_image

# Initialize shared platform core engines
metrics_db = MetricsCollector()
runtime_engine = FunctionRuntime(metrics=metrics_db)
router_bus = EventRouter(runtime=runtime_engine)

# Register execution context routes
router_bus.register(TriggerRule("http", "process_order", functions.process_order.handler, timeout_s=10))
router_bus.register(TriggerRule("http", "resize_image", functions.resize_image.handler, timeout_s=15))
router_bus.register(TriggerRule("timer", "resize_image", functions.resize_image.handler, timeout_s=15))

# Instantiating interface bridges
app = create_http_gateway(router_bus)
cron_scheduler = TimerTrigger(router_bus)

@app.on_event("startup")
async def startup_event():
    # Register background chron loops
    cron_scheduler.register("resize_image", interval_seconds=8, payload={"bucket": "cron-backups", "key": "nightly.png"})
    cron_scheduler.start()
    print("[Platform] Serverless engine simulation online and running.")

@app.get("/metrics/summary/{function_name}")
def get_metrics(function_name: str):
    return metrics_db.summary(function_name)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
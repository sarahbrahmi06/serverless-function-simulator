import asyncio
import random
from typing import Dict, Any
from core.context import FunctionContext

async def handler(event: Dict[str, Any], context: FunctionContext) -> Dict:
    context.log("Order processing engine initiated validation loops")
    body = event.get("body", {})
    order_id = body.get("order_id", f"ORD-{random.randint(1000, 9999)}")
    items = body.get("items", [])

    if not items:
        context.log("Validation failed: empty product manifest array detected", "ERROR")
        return {"status": "error", "message": "Order execution context missing manifest items"}

    context.log(f"Processing database sync for {order_id} containing {len(items)} items")
    
    steps = [("validate_inventory", 0.05), ("calculate_pricing", 0.03), ("reserve_stock", 0.08)]
    results = {}
    for step_name, delay in steps:
        context.log(f"Executing workflow transaction step: {step_name}")
        await asyncio.sleep(delay)
        results[step_name] = "completed"

    total = sum(item.get("price", 0) * item.get("qty", 1) for item in items)
    context.log(f"Order {order_id} committed successfully. Total: ${total:.2f}")

    return {
        "status": "success",
        "order_id": order_id,
        "total": round(total, 2),
        "steps_executed": results,
        "remaining_time_ms": context.get_remaining_time_ms()
    }
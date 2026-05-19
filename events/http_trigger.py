from fastapi import FastAPI, Request, HTTPException
from typing import Any, Dict
from core.event_router import EventRouter

def create_http_gateway(router: EventRouter) -> FastAPI:
    app = FastAPI(title="Serverless Simulation Gateway", version="1.0.0")

    @app.post("/functions/{function_name}/invoke")
    async def invoke_function(function_name: str, request: Request) -> Dict[str, Any]:
        try:
            body = await request.json()
        except Exception:
            body = {}

        event = {
            "trigger": "http",
            "method": request.method,
            "path": f"/functions/{function_name}/invoke",
            "headers": dict(request.headers),
            "body": body,
        }

        # Dispatch the payload down to the router bus matching the 'http' type
        results = await router.dispatch("http", event, target_function=function_name)
        
        # FIX: Check if the function failed to execute or doesn't exist in the router registry
        if not results or (isinstance(results[0], dict) and "error" in results[0] and results[0]["error"] is not None and results[0]["status"] == "error"):
            raise HTTPException(status_code=404, detail=f"Target serverless function '{function_name}' not found.")
            
        return results[0]

    @app.get("/functions")
    async def list_functions():
        registered = {}
        for trigger_type, rules in router._registry.items():
            for rule in rules:
                registered[rule.function_name] = {"trigger": trigger_type, "timeout": rule.timeout_s}
        return {"functions": registered, "count": len(registered)}

    return app
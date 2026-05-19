# Serverless Function Simulation Project

## Event-Driven Computing, Execution Monitoring, and Resource Analysis in Cloud Environments

---

## 📋 Project Overview

This project implements a complete serverless function simulation environment using a custom Python-based FaaS (Function-as-a-Service) runtime engine. The system demonstrates key serverless computing concepts including event-driven execution, cold start behavior, container reuse, resource monitoring, and decoupled messaging.

### Key Features

-  **HTTP Triggers** - REST API gateway using FastAPI
-  **SQS Queue Triggers** - Decoupled messaging with LocalStack
-  **Timer/Cron Triggers** - Scheduled function execution
-  **Cold Start Simulation** - 350ms overhead on first invocation
-  **Warm Container Pool** - Zero overhead on subsequent calls
-  **Resource Monitoring** - Memory usage, duration tracking
-  **Telemetry Aggregation** - p50 latency, cold start rates
-  **Structured Logging** - JSON logs with invocation IDs

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Cold Start Overhead | 350 ms |
| Warm Execution Overhead | 0 ms |
| Memory Peak | 45.71 MB |
| P50 Latency | 161.73 ms |
| Cold Start Rate (2 calls) | 50% |

---

##  Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core runtime |
| FastAPI | HTTP gateway |
| Uvicorn | ASGI server |
| LocalStack | AWS SQS emulation |
| psutil | Memory monitoring |
| asyncio | Async execution |
| boto3 | SQS client |

---

##  Project Structure

<img width="412" height="824" alt="image" src="https://github.com/user-attachments/assets/d4c8372f-b6eb-4b9f-b253-80f01c6ef489" />
<img width="942" height="447" alt="image" src="https://github.com/user-attachments/assets/004d4b9e-edb8-4b69-816c-f8a11125bffb" />



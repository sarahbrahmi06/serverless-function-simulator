import asyncio
import boto3
import json
from typing import Any, Dict
from core.event_router import EventRouter

class QueueTrigger:
    def __init__(self, router: EventRouter, queue_name: str, endpoint_url: str = "http://localhost:4566"):
        self.router = router
        self.queue_name = queue_name
        # Connect to our local containerized AWS SQS emulation layer
        self.sqs = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            region_name="us-east-1",
            aws_access_key_id="mock",
            aws_secret_access_key="mock"
        )
        self.queue_url = None
        self._running = False

    def initialize_queue(self):
        """Creates the SQS Queue in LocalStack if it doesn't exist."""
        try:
            response = self.sqs.create_queue(QueueName=self.queue_name)
            self.queue_url = response["QueueUrl"]
            print(f"[Queue] SQS Pipeline Connected successfully: {self.queue_url}")
        except Exception as e:
            print(f"[Queue] Initialization Error: {e}")

    async def start_polling(self):
        """Long-polls the SQS queue for incoming event payloads."""
        if not self.queue_url:
            self.initialize_queue()
        
        self._running = True
        print(f"[Queue] Polling daemon started. Listening for messages on '{self.queue_name}'...")

        while self._running:
            try:
                # Use standard asyncio loop to offload the blocking SQS network call
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=2  # Long polling interval
                ))

                messages = response.get("Messages", [])
                for msg in messages:
                    try:
                        body = json.loads(msg["Body"])
                    except Exception:
                        body = {"raw_payload": msg["Body"]}

                    event = {
                        "trigger": "queue",
                        "message_id": msg["MessageId"],
                        "receipt_handle": msg["ReceiptHandle"],
                        "body": body
                    }

                    print(f"[Queue] Decoupled Event Detected! Message ID: {msg['MessageId']}")
                    
                    # Route to our order processing engine
                    await self.router.dispatch("queue", event, "process_order")

                    # Delete message from queue after processing to prevent duplicates
                    await loop.run_in_executor(None, lambda: self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    ))
            except Exception as e:
                print(f"[Queue] Polling Error: {e}")
            
            await asyncio.sleep(1)

    def stop(self):
        self._running = False
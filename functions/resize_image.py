import os
import time
import json
import boto3
from botocore.config import Config

def handler(event, context):
    """
    Serverless function handler for media optimization and image resizing.
    Listens to cron timer events and processes target images via S3.
    """
    # Safe extraction tool: Works whether context is an object class OR a dictionary
    req_id = getattr(context, "request_id", "stub") if not isinstance(context, dict) else context.get("request_id", "stub")
    req_short = req_id[:8] if req_id else "stub"

    print(f"[INFO] resize_image ({req_short}...) INIT | cold_start=False")
    print(f"[INFO] resize_image ({req_short}...) Media optimization automation handler spawned successfully")

    # Extract target metadata parameters from the incoming event payload
    bucket_name = event.get("bucket", "cron-backups")
    file_key = event.get("key", "nightly.png")
    
    print(f"[INFO] resize_image ({req_short}...) Fetching raw file stream from: s3://{bucket_name}/{file_key}")
    
    # Configure botocore to release keep-alive TCP connections aggressively
    session_config = Config(
        max_pool_connections=1,
        retries={'max_attempts': 1}
    )

    # Initialize the client outside the 'with' block to support all boto3 iterations
    s3_client = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="mock",
        aws_secret_access_key="mock",
        config=session_config
    )

    try:
        # Simulated read hook from LocalStack S3 Storage layer
        time.sleep(0.1) 
        
        print(f"[INFO] resize_image ({req_short}...) Completed transform pipeline for target key resolution matrix 'thumb'")
        
        # Simulated write hook back to S3 for the processed thumbnail matrix
        time.sleep(0.1)

        return {
            "status": "success",
            "transformed_key": f"thumbnails/{file_key}",
            "matrix_resolution": "thumb",
            "processed_at": int(time.time())
        }

    except Exception as e:
        error_msg = f"Failed during pipeline transform execution: {str(e)}"
        print(f"[ERROR] resize_image ({req_short}...) {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }
        
    finally:
        # CRITICAL FIX: The finally block ALWAYS runs even if the code succeeds or crashes.
        # This forcefully closes the network connection pool so the serverless engine doesn't hang!
        try:
            s3_client.close()
        except AttributeError:
            pass # Handles older boto3 versions where close() doesn't exist
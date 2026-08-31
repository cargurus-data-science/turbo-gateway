import json
import os

import boto3

_sqs = boto3.client("sqs")
_queue_url = os.environ["QUEUE_URL"]


def handler(event, context):
    body = event.get("body") or ""

    _sqs.send_message(
        QueueUrl=_queue_url,
        MessageBody=body,
    )

    return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

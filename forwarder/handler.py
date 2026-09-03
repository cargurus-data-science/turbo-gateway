import hashlib
import hmac
import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_sqs = boto3.client("sqs")
_sm = boto3.client("secretsmanager")
_queue_url = os.environ["QUEUE_URL"]

_secret_cache: str | None = None


def _get_secret() -> str:
    global _secret_cache
    if _secret_cache is None:
        resp = _sm.get_secret_value(SecretId=os.environ["WEBHOOK_SECRET_NAME"])
        _secret_cache = resp["SecretString"]
    return _secret_cache


def handler(event, context):
    logger.info("Input event: %s", json.dumps(event))

    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    signature_header = headers.get("x-webhook-signature", "")
    body = event.get("body") or ""

    if not signature_header.startswith("sha256="):
        response = {"statusCode": 401, "body": json.dumps({"error": "missing signature"})}
        logger.info("Output: %s", response)
        return response

    expected = signature_header[len("sha256="):]
    secret = _get_secret()

    computed = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, expected):
        response = {"statusCode": 401, "body": json.dumps({"error": "invalid signature"})}
        logger.info("Output: %s", response)
        return response

    _sqs.send_message(
        QueueUrl=_queue_url,
        MessageBody=body,
    )

    response = {"statusCode": 200, "body": json.dumps({"status": "ok"})}
    logger.info("Output: %s", response)
    return response

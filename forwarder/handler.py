import hashlib
import hmac
import json
import os

import boto3

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
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    signature_header = headers.get("x-webhook-signature", "")
    body = event.get("body") or ""

    if not signature_header.startswith("sha256="):
        return {"statusCode": 401, "body": json.dumps({"error": "missing signature"})}

    expected = signature_header[len("sha256="):]
    secret = _get_secret()

    computed = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, expected):
        return {"statusCode": 401, "body": json.dumps({"error": "invalid signature"})}

    _sqs.send_message(
        QueueUrl=_queue_url,
        MessageBody=body,
    )

    return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

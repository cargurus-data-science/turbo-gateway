import ipaddress
import json
import os

# ALLOWED_IPS: comma-separated list of individual IPs or CIDR ranges.
# Examples: "52.3.77.232,192.30.252.0/22,185.199.108.0/22"
_raw = os.environ.get("ALLOWED_IPS", "").split(",")
ALLOWED_NETWORKS = []
for entry in _raw:
    entry = entry.strip()
    if not entry:
        continue
    try:
        ALLOWED_NETWORKS.append(ipaddress.ip_network(entry, strict=False))
    except ValueError:
        print(json.dumps({"warning": f"invalid IP/CIDR in allowlist: {entry!r}"}))


def _is_allowed(source_ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(source_ip)
    except ValueError:
        return False
    return any(addr in net for net in ALLOWED_NETWORKS)


def handler(event, context):
    source_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "")
    is_authorized = _is_allowed(source_ip)
    print(
        json.dumps(
            {
                "source_ip": source_ip,
                "is_authorized": is_authorized,
            }
        )
    )
    return {"isAuthorized": is_authorized}

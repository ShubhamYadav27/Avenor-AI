import hmac
import hashlib
import json
from typing import Dict, Any

def generate_signature(payload: Dict[str, Any], timestamp: str, secret: str) -> str:
    """
    Generates a Stripe-like HMAC SHA-256 signature for webhooks.
    Signature payload is `timestamp.json_payload`
    """
    # Use exact serialization format to ensure repeatable hash
    serialized_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    signed_payload = f"{timestamp}.{serialized_payload}"
    
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=signed_payload.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return mac.hexdigest()

def verify_signature(payload: Dict[str, Any], timestamp: str, signature: str, secret: str) -> bool:
    """Verifies an incoming signature using constant-time comparison."""
    expected_sig = generate_signature(payload, timestamp, secret)
    return hmac.compare_digest(expected_sig, signature)

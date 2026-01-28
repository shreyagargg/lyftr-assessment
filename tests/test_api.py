import hmac
import hashlib
import requests
import json
from datetime import datetime

# Configuration - Match your .env file
SECRET = "testsecret"
URL = "http://127.0.0.1:8000/webhook"

def send_webhook(msg_id, text):
    payload = {
        "message_id": msg_id,
        "from": "+919876543210",
        "to": "+14155550100",
        "ts": datetime.utcnow().isoformat() + "Z",
        "text": text
    }
    
    body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
    # Calculate HMAC-SHA256 signature
    signature = hmac.new(
        SECRET.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }

    response = requests.post(URL, data=body_bytes, headers=headers)
    print(f"Status: {response.status_code}, Body: {response.json()}")

if __name__ == "__main__":
    print("--- Testing Webhook Ingestion ---")
    send_webhook("msg_001", "Hello Lyftr!")
    
    print("\n--- Testing Idempotency (Sending same ID again) ---")
    send_webhook("msg_001", "Hello Lyftr!")
    
    print("\n--- Testing New Message ---")
    send_webhook("msg_002", "This is a second message")
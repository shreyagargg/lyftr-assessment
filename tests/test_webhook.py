import hmac, hashlib, requests, json
from datetime import datetime

URL = "http://127.0.0.1:8000/webhook"
SECRET = "testsecret" # Must match your .env

def test_webhook(msg_id, text, secret_to_use):
    payload = {
        "message_id": msg_id,
        "from": "+919876543210",
        "to": "+14155550100",
        "ts": datetime.utcnow().isoformat() + "Z",
        "text": text
    }
    body = json.dumps(payload, separators=(',', ':')).encode()
    signature = hmac.new(secret_to_use.encode(), body, hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json", "X-Signature": signature}
    
    res = requests.post(URL, data=body, headers=headers)
    print(f"ID: {msg_id} | Status: {res.status_code} | Response: {res.json()}")

print("--- 1. Testing Valid Ingestion ---")
test_webhook("order_101", "Valid message", SECRET)

print("\n--- 2. Testing Security (Wrong Secret) ---")
test_webhook("order_102", "Hack attempt", "wrong_secret")

print("\n--- 3. Testing Idempotency (Same ID again) ---")
test_webhook("order_101", "Duplicate message", SECRET)
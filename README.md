# 📩 Message Ingestion Service (Lyftr Assessment)

A production-style FastAPI service designed to ingest WhatsApp-like messages with high reliability, security, and observability.

## 🚀 Features

* **Exactly-Once Processing**: Implements idempotency using unique `message_id` tracking to prevent duplicate data from retried webhook deliveries.
* **HMAC Security**: All `/webhook` requests are authenticated via HMAC-SHA256 signature verification to ensure data integrity and authenticity.
* **Full Observability**:
* **Structured Logging**: Emits machine-readable JSON logs for every request to ensure better traceability.
* **Metrics**: Provides a Prometheus-compatible `/metrics` endpoint to track request counts and error rates.


* **12-Factor Compliant**: Configuration is entirely managed via environment variables and `.env` files.
* **Containerized**: Fully compatible with Docker and Docker Compose for seamless deployment.

---

## 🛠 Setup & Installation

### 1. Local Development (Without Docker)

1. **Create a Virtual Environment**:
```powershell
python -m venv venv
.\venv\Scripts\Activate

```


2. **Install Dependencies**:
```powershell
pip install -r requirements.txt

```


3. **Configure Environment**:
Create a `.env` file in the root directory:
```env
APP_NAME=LyftrService
ENV=development
DATABASE_URL=sqlite:///./app.db
WEBHOOK_SECRET=your_shared_secret

```


4. **Run the Server**:
```powershell
uvicorn main:app --reload

```



### 2. Running with Docker (Recommended)

If you have Docker installed, simply run:

```powershell
docker compose up --build

```

The API will be available at `http://localhost:8000`.

---

## 📊 API Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/webhook` | `POST` | Ingests messages. Requires `X-Signature` header. |
| `/messages` | `GET` | Paginated list of messages with filters (`q`, `from_msisdn`). |
| `/stats` | `GET` | Analytics: total messages, unique senders, and unique recipients. |
| `/metrics` | `GET` | Prometheus-style request and error counters. |
| `/health/live` | `GET` | Liveness probe. |
| `/health/ready` | `GET` | Readiness probe (checks DB connectivity). |

---

## 🧪 Testing

To verify the service, you can run the provided test suite:

```powershell
# Test Webhook security and idempotency
python tests/test_webhook.py

# Test API listing and stats
python tests/test_api.py

```

WiFi Sublet Backend
Flask + SQLAlchemy REST API for a plug-and-play WiFi reselling platform:
customer picks a bandwidth plan → enters their phone number → gets an
M-Pesa STK push → pays → is issued a voucher and marked connected.
No signup/login anywhere in this flow.
Stack
Flask (app factory pattern, blueprints)
Flask-SQLAlchemy (SQLite by default, swap `DATABASE_URL` for Postgres)
`requests` for the Daraja (M-Pesa) API
pytest for tests
Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # or requirements.txt for prod

cp .env.example .env
# fill in MPESA_CONSUMER_KEY / MPESA_CONSUMER_SECRET / MPESA_SHORTCODE / MPESA_PASSKEY
# from https://developer.safaricom.co.ke (sandbox creds are free)

python seed.py        # creates tables + a few starter plans
python run.py          # runs on http://localhost:5000
```
Run tests: `pytest -v` (7 tests covering plan listing, admin auth, phone
normalization, and the full order → STK push → callback → voucher flow,
all mocked — no real Safaricom calls needed).
Exposing the callback locally
Safaricom needs a public HTTPS URL to POST the payment result to. For local
dev, run `ngrok http 5000` and set `MPESA_CALLBACK_URL` in `.env` to
`https://<your-ngrok-subdomain>.ngrok-free.app/api/mpesa/callback`.
Endpoints
Public (no auth) — this is the whole customer flow:
Method	Path	Purpose
GET	`/api/plans`	List active plans (speed, price, duration)
GET	`/api/plans/<id>`	One plan's details
POST	`/api/orders`	`{plan_id, phone_number}` → creates order, fires STK push
GET	`/api/orders/<id>`	Full order detail
GET	`/api/orders/<id>/status`	Poll this from the frontend while waiting on payment
M-Pesa (Safaricom calls this, not your frontend):
Method	Path	Purpose
POST	`/api/mpesa/callback`	Daraja posts the payment result here
Admin (requires `X-Admin-Key` header matching `ADMIN_API_KEY`):
Method	Path	Purpose
GET	`/api/admin/plans`	List all plans, including inactive
POST	`/api/admin/plans`	Create a plan
PUT	`/api/admin/plans/<id>`	Update a plan
DELETE	`/api/admin/plans/<id>`	Deactivate (soft-delete) a plan
Example flow
```bash
# 1. Customer sees plans
curl http://localhost:5000/api/plans

# 2. Customer picks one and pays
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 2, "phone_number": "0712345678"}'
# -> {"order_id": 7, "status": "pending", "message": "Check your phone..."}

# 3. Frontend polls until paid
curl http://localhost:5000/api/orders/7/status
# -> {"order_id": 7, "status": "paid", "voucher_code": "K3P9X7QANZ"}
```
What's deliberately stubbed
`app/services/network_service.py::provision_connection()` is the hook that
runs the moment a payment clears. Right now it just logs — actually
turning the customer's internet on depends on your network setup
(Mikrotik hotspot, RADIUS, a captive portal, whatever you're running at
the edge), which is a separate piece of infrastructure. Wire that in
there once you've decided how the router side works.
Notes for going to production
Set a real `ADMIN_API_KEY` and `SECRET_KEY` (don't ship the defaults).
Point `DATABASE_URL` at Postgres — SQLite is fine for dev, not for concurrent writes under load.
`MpesaTransactionLog` keeps a raw copy of every STK request and callback — useful when a customer says "I paid but wasn't connected."
Consider a background job to sweep `pending` orders older than `ORDER_EXPIRY_MINUTES` into `expired`, since not every STK push gets a callback (e.g. customer just doesn't respond).
The callback endpoint has no auth — Safaricom doesn't support signing these easily, so most integrations lock it down by IP allowlist at the reverse proxy instead.
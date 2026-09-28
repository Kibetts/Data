import base64
from datetime import datetime

import requests
from flask import current_app


class MpesaError(Exception):
    pass


def _get_access_token():
    consumer_key = current_app.config["MPESA_CONSUMER_KEY"]
    consumer_secret = current_app.config["MPESA_CONSUMER_SECRET"]
    url = f"{current_app.config['MPESA_BASE_URL']}/oauth/v1/generate?grant_type=client_credentials"

    resp = requests.get(url, auth=(consumer_key, consumer_secret), timeout=15)
    if resp.status_code != 200:
        raise MpesaError(f"Failed to get access token: {resp.text}")
    return resp.json()["access_token"]


def _build_password(shortcode, passkey, timestamp):
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    """Triggers the Lipa na M-Pesa Online (STK push) prompt on the customer's phone.
    phone_number must already be normalized to 254XXXXXXXXX."""
    cfg = current_app.config
    token = _get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = _build_password(cfg["MPESA_SHORTCODE"], cfg["MPESA_PASSKEY"], timestamp)

    payload = {
        "BusinessShortCode": cfg["MPESA_SHORTCODE"],
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": cfg["MPESA_TRANSACTION_TYPE"],
        "Amount": int(round(float(amount))),  # Daraja rejects decimal amounts
        "PartyA": phone_number,
        "PartyB": cfg["MPESA_SHORTCODE"],
        "PhoneNumber": phone_number,
        "CallBackURL": cfg["MPESA_CALLBACK_URL"],
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    url = f"{cfg['MPESA_BASE_URL']}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    data = resp.json()

    if resp.status_code != 200 or data.get("ResponseCode") != "0":
        raise MpesaError(data.get("errorMessage") or data.get("ResponseDescription") or "STK push failed")

    return data  # contains MerchantRequestID, CheckoutRequestID, CustomerMessage

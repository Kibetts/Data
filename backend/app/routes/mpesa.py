import json

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import MpesaTransactionLog, Order
from app.services.network_service import provision_connection

mpesa_bp = Blueprint("mpesa", __name__)


@mpesa_bp.post("/callback")
def stk_callback():
    """Safaricom posts here after the customer accepts/cancels/fails the STK
    prompt. Always return 200 with ResultCode 0 quickly — Daraja retries on
    anything else, which can double-process a payment if you're not careful."""
    payload = request.get_json(silent=True) or {}
    stk_data = payload.get("Body", {}).get("stkCallback", {})

    checkout_request_id = stk_data.get("CheckoutRequestID")
    result_code = stk_data.get("ResultCode")
    result_desc = stk_data.get("ResultDesc")

    order = Order.query.filter_by(checkout_request_id=checkout_request_id).first()

    if order is None:
        # Nothing to match it to — log it anyway so nothing silently vanishes.
        db.session.add(MpesaTransactionLog(order_id=None, direction="callback", raw_payload=json.dumps(payload)))
        db.session.commit()
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    db.session.add(
        MpesaTransactionLog(order_id=order.id, direction="callback", raw_payload=json.dumps(payload))
    )

    # Idempotency guard: Daraja can redeliver the same callback.
    if order.status.value == "paid":
        db.session.commit()
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    if result_code == 0:
        metadata = {
            item["Name"]: item.get("Value")
            for item in stk_data.get("CallbackMetadata", {}).get("Item", [])
        }
        receipt_number = metadata.get("MpesaReceiptNumber")
        order.mark_paid(receipt_number=receipt_number, result_code=result_code, result_desc=result_desc)
        db.session.commit()
        provision_connection(order)
    else:
        order.mark_failed(result_code=result_code, result_desc=result_desc)
        db.session.commit()

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

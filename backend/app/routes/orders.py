import json

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import MpesaTransactionLog, Order, OrderStatus, Plan
from app.services.mpesa_service import MpesaError, initiate_stk_push
from app.utils.validators import ValidationError, normalize_phone

orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
def create_order():
    """Customer picks a plan and submits their phone number. This creates the
    order, fires the STK push, and returns immediately — the frontend should
    then poll GET /api/orders/<id>/status until it flips to paid/failed."""
    data = request.get_json(silent=True) or {}
    plan_id = data.get("plan_id")
    raw_phone = data.get("phone_number")

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    plan = db.session.get(Plan, plan_id)
    if not plan or not plan.is_active:
        return jsonify({"error": "Plan not found or unavailable"}), 404

    try:
        phone = normalize_phone(raw_phone)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    order = Order(plan_id=plan.id, phone_number=phone, amount=plan.price_kes, status=OrderStatus.PENDING)
    db.session.add(order)
    db.session.commit()

    try:
        stk_response = initiate_stk_push(
            phone_number=phone,
            amount=plan.price_kes,
            account_reference=f"ORDER{order.id}",
            transaction_desc=f"{plan.name} WiFi plan",
        )
    except MpesaError as e:
        order.mark_failed(result_code=-1, result_desc=str(e))
        db.session.commit()
        return jsonify({"error": f"Could not initiate payment: {e}"}), 502

    order.merchant_request_id = stk_response.get("MerchantRequestID")
    order.checkout_request_id = stk_response.get("CheckoutRequestID")
    db.session.add(
        MpesaTransactionLog(order_id=order.id, direction="request", raw_payload=json.dumps(stk_response))
    )
    db.session.commit()

    return (
        jsonify(
            {
                "order_id": order.id,
                "status": order.status.value,
                "message": "Check your phone and enter your M-Pesa PIN to complete payment.",
            }
        ),
        201,
    )


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@orders_bp.get("/<int:order_id>/status")
def get_order_status(order_id):
    """Lightweight endpoint for the frontend to poll while the STK push is pending."""
    order = Order.query.get_or_404(order_id)
    return jsonify(
        {
            "order_id": order.id,
            "status": order.status.value,
            "voucher_code": order.voucher_code if order.status == OrderStatus.PAID else None,
        }
    )

from flask import Blueprint, jsonify

from app.models import Plan

plans_bp = Blueprint("plans", __name__)


@plans_bp.get("")
def list_plans():
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.price_kes.asc()).all()
    return jsonify([p.to_dict() for p in plans])


@plans_bp.get("/<int:plan_id>")
def get_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    if not plan.is_active:
        return jsonify({"error": "Plan is not available"}), 404
    return jsonify(plan.to_dict())

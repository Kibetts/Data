from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Plan
from app.utils.decorators import require_admin_key

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/plans")
@require_admin_key
def list_all_plans():
    """Unlike GET /api/plans, this includes inactive plans — for the dashboard."""
    plans = Plan.query.order_by(Plan.id.asc()).all()
    return jsonify([p.to_dict() for p in plans])


@admin_bp.post("/plans")
@require_admin_key
def create_plan():
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("name", "speed_mbps", "price_kes") if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    plan = Plan(
        name=data["name"],
        speed_mbps=data["speed_mbps"],
        price_kes=data["price_kes"],
        duration_hours=data.get("duration_hours", 24),
        description=data.get("description"),
        is_active=data.get("is_active", True),
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@admin_bp.put("/plans/<int:plan_id>")
@require_admin_key
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}

    for field in ("name", "speed_mbps", "price_kes", "duration_hours", "description", "is_active"):
        if field in data:
            setattr(plan, field, data[field])

    db.session.commit()
    return jsonify(plan.to_dict())


@admin_bp.delete("/plans/<int:plan_id>")
@require_admin_key
def deactivate_plan(plan_id):
    """Soft delete — existing orders still reference this plan, so we don't hard-delete it."""
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = False
    db.session.commit()
    return jsonify({"message": "Plan deactivated"})

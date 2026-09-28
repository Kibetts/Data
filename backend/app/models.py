import enum
import secrets
import string
from datetime import datetime, timedelta, timezone

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    speed_mbps = db.Column(db.Integer, nullable=False)
    price_kes = db.Column(db.Numeric(10, 2), nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False, default=24)  # length of the access window
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    orders = db.relationship("Order", backref="plan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "speed_mbps": self.speed_mbps,
            "price_kes": float(self.price_kes),
            "duration_hours": self.duration_hours,
            "description": self.description,
            "is_active": self.is_active,
        }


def generate_voucher_code(length=10):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)

    phone_number = db.Column(db.String(15), nullable=False)  # normalized 2547XXXXXXXX
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)

    # Daraja STK push correlation ids, used to match the async callback back to this order
    merchant_request_id = db.Column(db.String(64))
    checkout_request_id = db.Column(db.String(64), index=True)

    # Populated once Safaricom confirms payment
    mpesa_receipt_number = db.Column(db.String(30))
    result_code = db.Column(db.Integer)
    result_desc = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime)

    # Issued once payment clears — this is what "connects" the customer
    voucher_code = db.Column(db.String(20), unique=True)
    connected_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    transactions = db.relationship("MpesaTransactionLog", backref="order", lazy="dynamic")

    def mark_paid(self, receipt_number, result_code, result_desc):
        self.status = OrderStatus.PAID
        self.mpesa_receipt_number = receipt_number
        self.result_code = result_code
        self.result_desc = result_desc
        self.paid_at = utcnow()
        self.voucher_code = generate_voucher_code()
        self.connected_at = utcnow()
        self.expires_at = utcnow() + timedelta(hours=self.plan.duration_hours)

    def mark_failed(self, result_code, result_desc):
        self.status = OrderStatus.FAILED
        self.result_code = result_code
        self.result_desc = result_desc

    def to_dict(self):
        return {
            "id": self.id,
            "plan": self.plan.to_dict() if self.plan else None,
            "phone_number": self.phone_number,
            "amount": float(self.amount),
            "status": self.status.value,
            "mpesa_receipt_number": self.mpesa_receipt_number,
            "voucher_code": self.voucher_code if self.status == OrderStatus.PAID else None,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
        }


class MpesaTransactionLog(db.Model):
    """Raw audit trail of every STK push request/callback — this is what you'll
    lean on when reconciling a customer's 'I paid but wasn't connected' complaint."""

    __tablename__ = "mpesa_transaction_logs"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    direction = db.Column(db.String(10), nullable=False)  # "request" | "callback"
    raw_payload = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'wifi_sublet.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Protects plan management + admin overrides. The customer-facing flow
    # itself (browse plans, pay, get connected) intentionally needs no auth.
    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "change-me-admin-key")

    # M-Pesa Daraja API (Lipa na M-Pesa Online / STK Push)
    MPESA_ENV = os.environ.get("MPESA_ENV", "sandbox")  # "sandbox" | "production"
    MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY", "")
    MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET", "")
    MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE", "")  # Paybill or Till number
    MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY", "")
    MPESA_CALLBACK_URL = os.environ.get("MPESA_CALLBACK_URL", "")  # public HTTPS URL -> /api/mpesa/callback
    MPESA_TRANSACTION_TYPE = os.environ.get("MPESA_TRANSACTION_TYPE", "CustomerPayBillOnline")

    MPESA_BASE_URL = (
        "https://api.safaricom.co.ke" if MPESA_ENV == "production" else "https://sandbox.safaricom.co.ke"
    )

    # How long an unpaid order can sit before you treat it as abandoned
    ORDER_EXPIRY_MINUTES = int(os.environ.get("ORDER_EXPIRY_MINUTES", 10))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MPESA_SHORTCODE = "174379"
    MPESA_PASSKEY = "test-passkey"
    MPESA_CALLBACK_URL = "https://example.com/api/mpesa/callback"

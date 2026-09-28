from flask import Flask

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes.admin import admin_bp
    from app.routes.mpesa import mpesa_bp
    from app.routes.orders import orders_bp
    from app.routes.plans import plans_bp

    app.register_blueprint(plans_bp, url_prefix="/api/plans")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(mpesa_bp, url_prefix="/api/mpesa")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app

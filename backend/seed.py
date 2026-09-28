"""Seed a handful of starter plans. Run with: python seed.py"""
from app import create_app
from app.extensions import db
from app.models import Plan

app = create_app()

PLANS = [
    {"name": "Lite", "speed_mbps": 5, "price_kes": 20, "duration_hours": 3, "description": "Quick browsing & chat"},
    {"name": "Standard", "speed_mbps": 10, "price_kes": 50, "duration_hours": 12, "description": "Streaming & video calls"},
    {"name": "Power", "speed_mbps": 20, "price_kes": 100, "duration_hours": 24, "description": "Heavy streaming & downloads"},
    {"name": "Power+", "speed_mbps": 40, "price_kes": 250, "duration_hours": 72, "description": "Multiple devices, 3-day pass"},
]

with app.app_context():
    db.create_all()
    for p in PLANS:
        if not Plan.query.filter_by(name=p["name"]).first():
            db.session.add(Plan(**p))
    db.session.commit()
    print(f"Seeded {len(PLANS)} plans.")

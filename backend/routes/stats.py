from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, Threat

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/stats")
def get_stats():
    total = db.session.query(func.count(Threat.id)).scalar()
    high = db.session.query(func.count(Threat.id)).filter_by(severity="high").scalar()
    medium = db.session.query(func.count(Threat.id)).filter_by(severity="medium").scalar()
    low = db.session.query(func.count(Threat.id)).filter_by(severity="low").scalar()

    return jsonify({
        "success": True,
        "data": {
            "total_threats": total,
            "high": high,
            "medium": medium,
            "low": low
        }
    })
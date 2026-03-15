from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from models import Threat
from extensions import db

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/stats")
@jwt_required()
def get_stats():
    total = db.session.query(func.count(Threat.id)).scalar()
    high = db.session.query(func.count(Threat.id)).filter_by(severity="high").scalar()
    medium = db.session.query(func.count(Threat.id)).filter_by(severity="medium").scalar()
    low = db.session.query(func.count(Threat.id)).filter_by(severity="low").scalar()

    return jsonify({
        "total_threats": total,
        "high": high,
        "medium": medium,
        "low": low
    })
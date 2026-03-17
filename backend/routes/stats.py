from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from models import Threat
from extensions import db
from datetime import datetime, timedelta

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/stats")
@jwt_required()
def get_stats():
    total = db.session.query(func.count(Threat.id)).scalar()
    high = db.session.query(func.count(Threat.id)).filter_by(severity="high").scalar()
    medium = db.session.query(func.count(Threat.id)).filter_by(severity="medium").scalar()
    low = db.session.query(func.count(Threat.id)).filter_by(severity="low").scalar()

    # Category distribution
    category_rows = db.session.query(Threat.category, func.count(Threat.id)).group_by(Threat.category).all()
    category_counts = [{"category": row[0] or "Unknown", "count": row[1]} for row in category_rows]

    # Trend over last 30 days (first_seen date)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=29)
    date_counts = { (start_date + timedelta(days=i)).isoformat(): 0 for i in range(30) }

    trends = db.session.query(Threat.first_seen).filter(Threat.first_seen >= start_date).all()
    for row in trends:
        dt = row[0]
        if dt:
            ds = dt.date().isoformat()
            if ds in date_counts:
                date_counts[ds] += 1

    return jsonify({
        "total_threats": total,
        "high": high,
        "medium": medium,
        "low": low,
        "categories": category_counts,
        "timeline": [{"date": date, "count": count} for date, count in sorted(date_counts.items())]
    })
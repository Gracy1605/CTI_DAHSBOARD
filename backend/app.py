from flask import Flask, jsonify, request
from models import db, Threat

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///threats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Backend is running with Database"

from flask import request
@app.route("/threats")
def get_threats():
    try:
        severity = request.args.get("severity")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive numbers"}), 400

        query = Threat.query

        if severity:
            if severity not in ["high", "medium", "low"]:
                return jsonify({"error": "Invalid severity value"}), 400
            query = query.filter_by(severity=severity)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "data": [t.to_dict() for t in pagination.items]
        })

    except Exception as e:
        return jsonify({"error": "Something went wrong"}), 500

@app.route("/stats")
def stats():
    total = Threat.query.count()
    high = Threat.query.filter_by(severity="high").count()
    medium = Threat.query.filter_by(severity="medium").count()
    low = Threat.query.filter_by(severity="low").count()

    result = {
        "total_threats": total,
        "high": high,
        "medium": medium,
        "low": low
    }

    return jsonify(result)

@app.route("/add-sample")
def add_sample():
    sample1 = Threat(
        ioc_type="ip",
        ioc_value="8.8.8.8",
        severity="high",
        category="malware",
        source="AlienVault"
    )

    sample2 = Threat(
        ioc_type="domain",
        ioc_value="example.com",
        severity="medium",
        category="phishing",
        source="AbuseIPDB"
    )

    db.session.add(sample1)
    db.session.add(sample2)
    db.session.commit()

    return "Sample data inserted!"

if __name__ == "__main__":
    app.run(debug=True)


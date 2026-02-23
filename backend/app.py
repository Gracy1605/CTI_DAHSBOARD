from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt,
    get_jwt_identity,
    create_access_token
)
from models import db, Threat
from routes.stats import stats_bp
from routes.auth import auth_bp

app = Flask(__name__)
CORS(app)

# ================= JWT CONFIG =================
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# ================= DATABASE CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///threats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ================= BLUEPRINTS =================
app.register_blueprint(stats_bp)
app.register_blueprint(auth_bp)

# ================= ROUTES =================

@app.route("/")
def home():
    return "Backend is running with Database + JWT"


# 🔐 PROTECTED THREATS ROUTE
@app.route("/threats")
@jwt_required()
def get_threats():
    try:
        severity = request.args.get("severity")
        search = request.args.get("search")
        sort_by = request.args.get("sort_by")
        order = request.args.get("order", "asc")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive numbers"}), 400

        query = Threat.query

        # Severity filter
        if severity:
            if severity not in ["high", "medium", "low"]:
                return jsonify({"error": "Invalid severity value"}), 400
            query = query.filter_by(severity=severity)

        # Search filter
        if search:
            query = query.filter(Threat.ioc_value.contains(search))

        # Sorting
        if sort_by == "severity":
            if order == "desc":
                query = query.order_by(Threat.severity.desc())
            else:
                query = query.order_by(Threat.severity.asc())

        if sort_by == "first_seen":
            if order == "desc":
                query = query.order_by(Threat.first_seen.desc())
            else:
                query = query.order_by(Threat.first_seen.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "data": [t.to_dict() for t in pagination.items]
        })

    except Exception:
        return jsonify({"error": "Something went wrong"}), 500


# 🔐 PROTECTED STATS ROUTE
@app.route("/stats")
@jwt_required()
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


# 🔐 ADMIN ONLY ROUTE
@app.route("/add-sample")
@jwt_required()
def add_sample():
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

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


# 🔁 REFRESH TOKEN ROUTE
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity)

    return jsonify({
        "access_token": new_access
    })


if __name__ == "__main__":
    app.run(debug=True)
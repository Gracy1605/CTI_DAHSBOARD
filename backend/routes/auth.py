from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token

auth_bp = Blueprint("auth", __name__)

# Temporary demo user
USER_DATA = {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
}

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No input data"}), 400

    username = data.get("username")
    password = data.get("password")

    if username != USER_DATA["username"] or password != USER_DATA["password"]:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=username,
        additional_claims={"role": USER_DATA["role"]}
    )

    refresh_token = create_refresh_token(identity=username)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200
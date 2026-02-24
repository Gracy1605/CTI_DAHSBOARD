from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token

auth_bp = Blueprint("auth", __name__)

# Temporary demo user
USER_DATA = {
    "username": "admin",
    "password": "admin123"
}

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if username == USER_DATA["username"] and password == USER_DATA["password"]:
        access_token = create_access_token(
            identity=username,
            additional_claims={"role": "admin"}
        )

        refresh_token = create_refresh_token(identity=username)
        )
        return jsonify({
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401
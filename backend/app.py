from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import threading
import time

from extensions import db, jwt
from config import Config
from models import Threat

from routes.stats import stats_bp
from routes.auth import auth_bp
from routes.threats import threats_bp

app = Flask(__name__)
CORS(app)

# ================= CONFIG =================
app.config.from_object(Config)

# ================= INIT EXTENSIONS =================
db.init_app(app)
jwt.init_app(app)

with app.app_context():
    db.create_all()

# ================= BLUEPRINTS =================
app.register_blueprint(stats_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(threats_bp)

# ================= BACKEND FUNCTION: AUTO-FETCH LIVE THREATS =================
def auto_fetch_live_threats(interval_minutes=10):
    """
    Background thread: fetch live threats from AlienVault OTX every `interval_minutes`.
    """
    def fetch_loop():
        while True:
            try:
                api_key = app.config.get("OTX_API_KEY")
                if not api_key:
                    print("No OTX API key configured")
                    return

                headers = {"X-OTX-API-KEY": api_key}
                url = "https://otx.alienvault.com/api/v1/pulses/subscribed?limit=20"
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    print(f"Failed to fetch OTX data: {resp.status_code}")
                    time.sleep(interval_minutes * 60)
                    continue

                data = resp.json()
                inserted = 0
                with app.app_context():
                    for pulse in data.get("results", []):
                        for indicator in pulse.get("indicators", []):
                            ioc_type = indicator.get("type")
                            ioc_value = indicator.get("indicator")

                            if not ioc_type or not ioc_value:
                                continue

                            # Normalize ioc_type
                            if ioc_type.lower() in ["ipv4", "ipv6"]:
                                ioc_type_norm = "ip"
                            elif ioc_type.lower() == "domain":
                                ioc_type_norm = "domain"
                            elif ioc_type.lower() in ["sha1", "sha256", "md5"]:
                                ioc_type_norm = "hash"
                            else:
                                ioc_type_norm = "other"

                            # Deduplicate
                            existing = Threat.query.filter_by(
                                ioc_type=ioc_type_norm, ioc_value=ioc_value
                            ).first()
                            if existing:
                                continue

                            # Add new threat
                            new_threat = Threat(
                                ioc_type=ioc_type_norm,
                                ioc_value=ioc_value,
                                severity="high",
                                category=pulse.get("name", "unknown"),
                                source="AlienVault",
                                first_seen=datetime.utcnow(),
                                last_seen=datetime.utcnow()
                            )
                            db.session.add(new_threat)
                            inserted += 1
                    if inserted > 0:
                        db.session.commit()
                        print(f"[AUTO-FETCH] Inserted {inserted} new threats")
            except Exception as e:
                print(f"[AUTO-FETCH] Error: {str(e)}")

            time.sleep(interval_minutes * 60)

    thread = threading.Thread(target=fetch_loop, daemon=True)
    thread.start()

# Start auto-fetch thread on backend start
auto_fetch_live_threats(interval_minutes=10)  # adjust interval as needed

# ================= ROUTES =================
@app.route("/")
def home():
    return "Backend is running with Database + JWT"

# ================= GLOBAL ERROR HANDLERS =================
@app.errorhandler(404)
def not_found(error):
    return {"success": False, "error": "Route not found"}, 404

@app.errorhandler(500)
def server_error(error):
    return {"success": False, "error": "Internal server error"}, 500

@app.errorhandler(400)
def bad_request(error):
    return {"success": False, "error": "Bad request"}, 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
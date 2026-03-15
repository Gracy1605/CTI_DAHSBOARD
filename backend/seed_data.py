from flask import Flask
from models import db, Threat
from config import Config
import random
from datetime import datetime, timedelta

# Create app instance
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
from extensions import db as _db, jwt
_db.init_app(app)
jwt.init_app(app)

severities = ["high", "medium", "low"]
categories = ["malware", "phishing", "ransomware", "botnet", "trojan", "spyware"]
sources = ["AlienVault", "AbuseIPDB", "MISP", "OTX", "VirusTotal"]
ioc_types = ["ip", "domain", "hash", "url", "email", "file"]

def generate_random_date():
    start_date = datetime(2025, 1, 1)
    random_days = random.randint(0, 365)
    return start_date + timedelta(days=random_days)

def generate_sample_ioc(ioc_type):
    if ioc_type == "ip":
        return f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
    elif ioc_type == "domain":
        domains = ["example.com", "test.org", "badguy.net", "malicious.io", "suspicious.biz"]
        return random.choice(domains)
    elif ioc_type == "hash":
        return f"{'a' * 32}{random.randint(1000,9999)}"  # fake hash
    elif ioc_type == "url":
        return f"http://malicious{random.randint(1,100)}.com/path"
    elif ioc_type == "email":
        return f"user{random.randint(1,100)}@bad{random.randint(1,100)}.com"
    elif ioc_type == "file":
        return f"malware{random.randint(1,100)}.exe"
    return "unknown"

with app.app_context():
    # Create tables
    _db.create_all()

    # Clear existing data
    _db.session.query(Threat).delete()
    _db.session.commit()

    for i in range(50):
        ioc_type = random.choice(ioc_types)
        ioc_value = generate_sample_ioc(ioc_type)
        first = generate_random_date()
        last = first + timedelta(days=random.randint(0, 30))

        threat = Threat(
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            severity=random.choice(severities),
            category=random.choice(categories),
            source=random.choice(sources),
            first_seen=first,
            last_seen=last
        )

        _db.session.add(threat)

    _db.session.commit()

print("50 diverse threats inserted successfully!")
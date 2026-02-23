from app import app
from models import db, Threat
import random
from datetime import datetime, timedelta

severities = ["high", "medium", "low"]
categories = ["malware", "phishing", "ransomware", "botnet"]
sources = ["AlienVault", "AbuseIPDB", "MISP", "OTX"]

def generate_random_date():
    start_date = datetime(2025, 1, 1)
    random_days = random.randint(0, 365)
    return start_date + timedelta(days=random_days)

with app.app_context():
    for i in range(300):
        first = generate_random_date()
        last = first + timedelta(days=random.randint(0, 30))

        threat = Threat(
            ioc_type=random.choice(["ip", "domain"]),
            ioc_value=f"192.168.1.{random.randint(1,255)}",
            severity=random.choice(severities),
            category=random.choice(categories),
            source=random.choice(sources),
            first_seen=first,
            last_seen=last
        )

        db.session.add(threat)

    db.session.commit()

print("300 threats inserted successfully!")
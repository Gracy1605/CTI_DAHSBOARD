from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running"


@app.route("/threats")
def threats():
    data = [
        {
            "id": 1,
            "ioc_type": "ip",
            "ioc_value": "8.8.8.8",
            "severity": "high",
            "category": "malware",
            "source": "AlienVault"
        },
        {
            "id": 2,
            "ioc_type": "domain",
            "ioc_value": "example.com",
            "severity": "medium",
            "category": "phishing",
            "source": "AbuseIPDB"
        }
    ]
    return jsonify(data)


@app.route("/stats")
def stats():
    threats = [
        {"severity": "high"},
        {"severity": "medium"}
    ]

    result = {
        "total_threats": len(threats),
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for t in threats:
        if t["severity"] == "high":
            result["high"] += 1
        elif t["severity"] == "medium":
            result["medium"] += 1
        elif t["severity"] == "low":
            result["low"] += 1

    return jsonify(result)


if __name__ == "__main__":
    app.run()
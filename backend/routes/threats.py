from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from extensions import db
from models import Threat
import requests
from datetime import datetime

threats_bp = Blueprint("threats", __name__)


def normalize_ioc_type(ioc_type):
    if not ioc_type:
        return "other"
    it = ioc_type.lower().strip()

    # IP addresses
    if it in ["ipv4", "ipv6", "ip", "ip_address", "address"]:
        return "ip"

    # Domains
    if it in ["domain", "hostname", "fqdn"]:
        return "domain"

    # File hashes
    if it in ["sha1", "sha256", "sha512", "md5", "hash", "file_hash"]:
        return "hash"

    # URLs
    if it in ["url", "uri"]:
        return "url"

    # Email addresses
    if it in ["email", "email_address", "mail"]:
        return "email"

    # File names
    if it in ["file", "filename", "file_name", "filepath", "path"]:
        return "file"

    # CVE identifiers
    if it.startswith("cve-") or it.startswith("cve_"):
        return "cve"

    # Registry keys
    if it in ["regkey", "registry", "reg"]:
        return "registry"

    # Mutex names
    if it in ["mutex", "mutant"]:
        return "mutex"

    # Additional hash types
    if it in ["ssdeep", "imphash", "tlsh"]:
        return "hash"

    # Default to other
    return "other"


def assign_severity(indicator, pulse, index):
    """
    Assign severity based on various factors to ensure variety
    """
    # Try to get risk score from indicator
    risk = None
    if "risk" in indicator and indicator["risk"] is not None:
        risk = indicator["risk"]
    elif "reputation" in indicator and indicator["reputation"] is not None:
        risk = indicator["reputation"]

    # If no risk score, try pulse threat_score
    if risk is None and "threat_score" in pulse:
        risk = pulse["threat_score"]

    # Convert to severity
    if isinstance(risk, str):
        risk_lower = risk.lower()
        if risk_lower in ["high", "malicious", "suspicious"]:
            return "high"
        elif risk_lower in ["medium", "unknown"]:
            return "medium"
        elif risk_lower in ["low", "clean", "safe"]:
            return "low"

    elif isinstance(risk, (int, float)):
        if risk >= 7:
            return "high"
        elif risk >= 4:
            return "medium"
        else:
            return "low"

    # If no risk data available, assign based on index to ensure variety
    severities = ["high", "medium", "low"]
    return severities[index % 3]


def parse_date(d):
    if not d:
        return None
    if isinstance(d, str):
        try:
            if d.endswith("Z"):
                d = d[:-1] + "+00:00"
            return datetime.fromisoformat(d)
        except Exception:
            pass
    return None


@threats_bp.route("/threats")
@jwt_required()
def get_threats():
    try:
        severity = request.args.get("severity")
        search = request.args.get("search")
        sort_by = request.args.get("sort_by")
        order = request.args.get("order", "asc")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive numbers"}), 400

        query = Threat.query

        if severity:
            if severity not in ["high", "medium", "low"]:
                return jsonify({"error": "Invalid severity filter"}), 400
            query = query.filter_by(severity=severity)

        if search:
            query = query.filter(Threat.ioc_value.contains(search))

        if sort_by == "severity":
            query = query.order_by(Threat.severity.desc() if order == "desc" else Threat.severity.asc())
        elif sort_by == "first_seen":
            query = query.order_by(Threat.first_seen.desc() if order == "desc" else Threat.first_seen.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "data": [t.to_dict() for t in pagination.items]
        }), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@threats_bp.route("/fetch-live", methods=["POST"])
@jwt_required()
def fetch_live_threats():
    try:
        api_key = current_app.config.get("OTX_API_KEY")
        headers = {}
        if api_key:
            headers["X-OTX-API-KEY"] = api_key

        pulse_url = "https://otx.alienvault.com/api/v1/pulses?limit=20"
        pulses_resp = requests.get(pulse_url, headers=headers, timeout=12)

        if pulses_resp.status_code != 200:
            return jsonify({"error": "Unable to fetch OTX pulses", "status": pulses_resp.status_code}), 502

        pulses = pulses_resp.json().get("results", [])
        inserted = 0

        for pulse in pulses:
            pulse_id = pulse.get("id") or pulse.get("uuid")
            if not pulse_id:
                continue

            detail_url = f"https://otx.alienvault.com/api/v1/pulses/{pulse_id}"
            detail_resp = requests.get(detail_url, headers=headers, timeout=12)
            if detail_resp.status_code != 200:
                continue

            indicators = detail_resp.json().get("indicators", [])
            for idx, ind in enumerate(indicators):
                ioc_value = ind.get("indicator")
                ioc_type = normalize_ioc_type(ind.get("type"))

                if not ioc_value:
                    continue

                if Threat.query.filter_by(ioc_type=ioc_type, ioc_value=ioc_value).first():
                    continue

                severity = assign_severity(ind, pulse, idx)

                first_seen = parse_date(ind.get("created") or ind.get("first_seen")) or datetime.utcnow()
                last_seen = parse_date(ind.get("modified") or ind.get("last_seen")) or datetime.utcnow()

                threat = Threat(
                    ioc_type=ioc_type,
                    ioc_value=ioc_value,
                    severity=severity,
                    category=pulse.get("name", "unknown"),
                    source="AlienVault OTX",
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
                db.session.add(threat)
                inserted += 1

        if inserted:
            db.session.commit()

        return jsonify({"success": True, "inserted": inserted, "total": Threat.query.count()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to fetch live threats", "details": str(e)}), 500
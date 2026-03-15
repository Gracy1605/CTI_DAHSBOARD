from datetime import datetime
from extensions import db

class Threat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ioc_type = db.Column(db.String(50), nullable=False)
    ioc_value = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100))
    source = db.Column(db.String(100))
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ioc_type": self.ioc_type,
            "ioc_value": self.ioc_value,
            "severity": self.severity,
            "category": self.category,
            "source": self.source,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }
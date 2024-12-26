from datetime import datetime
from ..database import db

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encoder_id = db.Column(db.Integer, db.ForeignKey('encoder.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False) 
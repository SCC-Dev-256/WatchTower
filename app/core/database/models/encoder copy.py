from datetime import datetime, timedelta
from app.core.database import db
from app.flask_models.alert import Alert
from app.flask_models.encoder_metric import EncoderMetrics

class Encoder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), default='offline')
    streaming = db.Column(db.Boolean, default=False)
    recording = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    alerts = db.relationship('Alert', backref='encoder', lazy=True)
    metrics = db.relationship('EncoderMetrics', backref='encoder', lazy=True)
    
    # Add helper methods
    def get_recent_alerts(self, hours=24):
        """Get alerts from the last 24 hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return Alert.query.filter_by(encoder_id=self.id)\
                        .filter(Alert.timestamp >= cutoff)\
                        .order_by(Alert.timestamp.desc())\
                        .all()
    
    def get_metrics_history(self, minutes=60):
        """Get metrics history for the last hour"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return EncoderMetrics.query.filter_by(encoder_id=self.id)\
                                 .filter(EncoderMetrics.timestamp >= cutoff)\
                                 .order_by(EncoderMetrics.timestamp.asc())\
                                 .all()
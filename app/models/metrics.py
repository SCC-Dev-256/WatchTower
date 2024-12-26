from datetime import datetime
from typing import Dict
from sqlalchemy.dialects.postgresql import JSON
from ..database import db

class EncoderMetrics(db.Model):
    """Consolidated encoder metrics model"""
    __tablename__ = 'encoder_metrics_v2'

    id = db.Column(db.Integer, primary_key=True)
    encoder_id = db.Column(db.Integer, db.ForeignKey('encoder.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Streaming metrics
    streaming_data = db.Column(JSON, nullable=True, default={})  # bitrate, fps, resolution, dropped_frames
    bandwidth = db.Column(db.Integer, nullable=True)  # Current bandwidth usage in bps
    
    # Storage metrics
    storage_used = db.Column(db.BigInteger, nullable=True)  # Bytes used
    storage_total = db.Column(db.BigInteger, nullable=True)  # Total bytes
    storage_health = db.Column(db.Integer, nullable=True)  # Health score 0-100
    
    # Network metrics
    network_stats = db.Column(JSON, nullable=True, default={})  # latency, packet_loss, jitter
    
    # System metrics
    system_stats = db.Column(JSON, nullable=True, default={})  # cpu, memory, temperature
    
    # Relationships
    encoder = db.relationship('Encoder', backref=db.backref('metrics', lazy=True))
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'id': self.id,
            'encoder_id': self.encoder_id,
            'timestamp': self.timestamp.isoformat(),
            'streaming': self.streaming_data,
            'bandwidth': self.bandwidth,
            'storage': {
                'used': self.storage_used,
                'total': self.storage_total,
                'health': self.storage_health
            },
            'network': self.network_stats,
            'system': self.system_stats
        }
    
    @classmethod
    def create_from_dict(cls, encoder_id: int, metrics_data: Dict) -> 'EncoderMetrics':
        """Create metrics instance from dictionary"""
        return cls(
            encoder_id=encoder_id,
            streaming_data=metrics_data.get('streaming', {}),
            bandwidth=metrics_data.get('bandwidth'),
            storage_used=metrics_data.get('storage', {}).get('used'),
            storage_total=metrics_data.get('storage', {}).get('total'),
            storage_health=metrics_data.get('storage', {}).get('health'),
            network_stats=metrics_data.get('network', {}),
            system_stats=metrics_data.get('system', {})
        ) 
from datetime import datetime
from sqlalchemy import Column, DateTime

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MetricsMixin:
    def get_metrics_dict(self):
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'bandwidth_usage': self.bandwidth_usage,
            'stream_health': self.stream_health
        } 
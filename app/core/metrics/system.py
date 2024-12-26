from typing import Dict, List
from datetime import datetime
from app.core.error_handling import handle_errors
from app.database import db
from app.models.metrics import EncoderMetrics
from app.core.metrics.analyzer import MetricsAnalyzer
from app.core.metrics.collector import MetricsCollector

class MetricsSystem:
    """Consolidated metrics system"""
    
    def __init__(self, app=None):
        self.app = app
        self.analyzer = MetricsAnalyzer()
        self.collector = MetricsCollector()
        
        if app:
            self.init_app(app)

    @handle_errors()
    async def collect_and_analyze(self, encoder_id: str) -> Dict:
        """Main entry point for metrics collection and analysis"""
        # Collect metrics
        metrics = await self.collector.collect_metrics(encoder_id)
        
        # Store metrics
        await self._store_metrics(encoder_id, metrics)
        
        # Analyze metrics
        analysis = await self.analyzer.analyze_metrics(metrics)
        
        return {
            'metrics': metrics,
            'analysis': analysis,
            'timestamp': datetime.utcnow()
        }

    async def _store_metrics(self, encoder_id: str, metrics: Dict):
        """Unified storage method"""
        metric = EncoderMetrics(
            encoder_id=encoder_id,
            streaming_data=metrics.get('streaming', {}),
            bandwidth=metrics.get('bandwidth'),
            storage_used=metrics.get('storage', {}).get('used'),
            storage_total=metrics.get('storage', {}).get('total'),
            storage_health=metrics.get('storage', {}).get('health')
        )
        db.session.add(metric)
        await db.session.commit() 
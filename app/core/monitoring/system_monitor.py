from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Counter, Gauge, Histogram
from app.core.error_handling import handle_errors
from app.core.database.models.encoder import EncoderMetrics
from app.core.logging.system import LoggingSystem
from app.core.database import db
from app.core.error_handling.handlers import MonitoringErrorHandler
from app.core.error_handling.error_logging import ErrorLogger

class EncoderMonitoringSystem:
    """Unified monitoring system"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = self._setup_metrics()
        self.logger = LoggingSystem(app)
        self.error_handler = MonitoringErrorHandler(app)
        self.thresholds = {
            'cpu_usage': 80,  # %
            'memory_usage': 85,  # %
            'temperature': 75,  # Celsius
            'storage_usage': 90,  # %
            'dropped_frames': 100,  # frames
            'latency': 1000,  # ms
        }
        
    def _setup_metrics(self) -> Dict:
        """Initialize Prometheus metrics"""
        return {
            'health': Gauge('encoder_health', 'Overall health score', 
                          ['encoder_id']),
            'temperature': Gauge('encoder_temperature', 'Device temperature', 
                               ['encoder_id']),
            'errors': Counter('encoder_errors', 'Error count', 
                            ['encoder_id', 'type']),
            'response_time': Histogram('encoder_response_time', 'API response time', 
                                     ['encoder_id']),
            'stream_health': Gauge('encoder_stream_health', 'Stream health score', 
                                 ['encoder_id', 'stream_id']),
            'storage_usage': Gauge('encoder_storage_usage', 'Storage usage percentage', 
                                 ['encoder_id'])
        }

    @handle_errors()
    async def monitor_encoder(self, encoder_id: str) -> Dict:
        """Comprehensive encoder monitoring"""
        start_time = datetime.utcnow()
        
        # Parallel collection of metrics and health data
        metrics_task = asyncio.create_task(self._collect_metrics(encoder_id))
        health_task = asyncio.create_task(self._check_health(encoder_id))
        
        metrics, health_status = await asyncio.gather(metrics_task, health_task)
        
        # Process alerts based on collected data
        alerts = await self._process_alerts(encoder_id, metrics, health_status)
        
        # Store monitoring data
        await self._store_monitoring_data(encoder_id, metrics, health_status)
        
        # Update response time metric
        response_time = (datetime.utcnow() - start_time).total_seconds()
        self.metrics['response_time'].labels(encoder_id=encoder_id).observe(response_time)
        
        return {
            'metrics': metrics,
            'health': health_status,
            'alerts': alerts,
            'timestamp': datetime.utcnow()
        }

    async def _collect_metrics(self, encoder_id: str) -> Dict:
        """Collect all encoder metrics"""
        try:
            # Collect system metrics
            system_metrics = await self._get_system_metrics(encoder_id)
            
            # Collect stream metrics
            stream_metrics = await self._get_stream_metrics(encoder_id)
            
            # Collect storage metrics
            storage_metrics = await self._get_storage_metrics(encoder_id)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(encoder_id, system_metrics, stream_metrics, storage_metrics)
            
            return {
                'system': system_metrics,
                'stream': stream_metrics,
                'storage': storage_metrics,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            await self.error_handler.handle_metric_error(encoder_id, 'metric_collection', e)
            raise

    async def _check_health(self, encoder_id: str) -> Dict:
        """Check encoder health status"""
        try:
            metrics = await self._collect_metrics(encoder_id)
            
            # Calculate health scores
            system_health = self._calculate_system_health(metrics['system'])
            stream_health = self._calculate_stream_health(metrics['stream'])
            storage_health = self._calculate_storage_health(metrics['storage'])
            
            # Calculate overall health score (weighted average)
            overall_health = (
                system_health['score'] * 0.4 +
                stream_health['score'] * 0.4 +
                storage_health['score'] * 0.2
            )
            
            # Update health metric
            self.metrics['health'].labels(encoder_id=encoder_id).set(overall_health)
            
            return {
                'overall_score': overall_health,
                'system_health': system_health,
                'stream_health': stream_health,
                'storage_health': storage_health,
                'issues': [
                    *system_health['issues'],
                    *stream_health['issues'],
                    *storage_health['issues']
                ]
            }
            
        except Exception as e:
            await self.error_handler.handle_metric_error(encoder_id, 'health_check', e)
            raise

    async def _process_alerts(self, encoder_id: str, 
                            metrics: Dict, health: Dict) -> List[Dict]:
        """Process and generate alerts"""
        alerts = []
        
        # Check system alerts
        if metrics['system']['cpu_usage'] > self.thresholds['cpu_usage']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f"High CPU usage: {metrics['system']['cpu_usage']}%"
            })
            
        if metrics['system']['temperature'] > self.thresholds['temperature']:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'message': f"High temperature: {metrics['system']['temperature']}°C"
            })
            
        # Check stream alerts
        if metrics['stream']['dropped_frames'] > self.thresholds['dropped_frames']:
            alerts.append({
                'type': 'stream',
                'severity': 'warning',
                'message': f"High dropped frames: {metrics['stream']['dropped_frames']}"
            })
            
        # Check storage alerts
        storage_usage = (metrics['storage']['used'] / metrics['storage']['total']) * 100
        if storage_usage > self.thresholds['storage_usage']:
            alerts.append({
                'type': 'storage',
                'severity': 'warning',
                'message': f"High storage usage: {storage_usage:.1f}%"
            })
            
        # Log alerts
        for alert in alerts:
            self.logger.log_event(
                'monitoring',
                'alert_generated',
                level=alert['severity'],
                encoder_id=encoder_id,
                alert_type=alert['type'],
                message=alert['message']
            )
            
        return alerts

    async def _store_monitoring_data(self, encoder_id: str, 
                                   metrics: Dict, health: Dict) -> None:
        """Store monitoring data in database"""
        metric = EncoderMetrics(
            encoder_id=encoder_id,
            streaming_data=metrics['stream'],
            system_stats=metrics['system'],
            storage_used=metrics['storage']['used'],
            storage_total=metrics['storage']['total'],
            storage_health=health['storage_health']['score']
        )
        
        db.session.add(metric)
        await db.session.commit()

    def _calculate_system_health(self, metrics: Dict) -> Dict:
        """Calculate system health score"""
        score = 100
        issues = []
        
        # CPU check
        if metrics['cpu_usage'] > self.thresholds['cpu_usage']:
            score -= 20
            issues.append('high_cpu_usage')
            
        # Memory check
        if metrics['memory_usage'] > self.thresholds['memory_usage']:
            score -= 20
            issues.append('high_memory_usage')
            
        # Temperature check
        if metrics['temperature'] > self.thresholds['temperature']:
            score -= 30
            issues.append('high_temperature')
            
        return {
            'score': max(score / 100, 0),
            'issues': issues
        }

    def _calculate_stream_health(self, metrics: Dict) -> Dict:
        """Calculate stream health score"""
        score = 100
        issues = []
        
        # Dropped frames check
        if metrics['dropped_frames'] > self.thresholds['dropped_frames']:
            score -= 25
            issues.append('high_dropped_frames')
            
        # Bitrate stability check
        if metrics.get('bitrate_variance', 0) > 0.2:
            score -= 25
            issues.append('unstable_bitrate')
            
        return {
            'score': max(score / 100, 0),
            'issues': issues
        }

    def _calculate_storage_health(self, metrics: Dict) -> Dict:
        """Calculate storage health score"""
        score = 100
        issues = []
        
        # Storage usage check
        usage_percent = (metrics['used'] / metrics['total']) * 100
        if usage_percent > self.thresholds['storage_usage']:
            score -= 30
            issues.append('high_storage_usage')
            
        return {
            'score': max(score / 100, 0),
            'issues': issues
        }

    def _update_prometheus_metrics(self, encoder_id: str, 
                                 system_metrics: Dict,
                                 stream_metrics: Dict,
                                 storage_metrics: Dict) -> None:
        """Update Prometheus metrics"""
        # Update system metrics
        self.metrics['temperature'].labels(
            encoder_id=encoder_id
        ).set(system_metrics['temperature'])
        
        # Update stream metrics
        self.metrics['stream_health'].labels(
            encoder_id=encoder_id,
            stream_id='main'
        ).set(stream_metrics.get('health_score', 0))
        
        # Update storage metrics
        storage_usage = (storage_metrics['used'] / storage_metrics['total']) * 100
        self.metrics['storage_usage'].labels(
            encoder_id=encoder_id
        ).set(storage_usage) 
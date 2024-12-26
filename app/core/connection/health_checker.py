from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Gauge, Counter
from app.core.connection.thermal_manager import ConnectionThermalManager
from app.core.rest_API_client import AJADevice
from app.models.encoder import HeloEncoder

class ConnectionHealthMetrics:
    """
    Metrics for monitoring HELO connection health.
    
    This class defines Prometheus metrics for tracking connection health status,
    check results, and performance indicators.

    Attributes:
        health_score (Gauge): Overall health score for connections
        health_checks (Counter): Count of health checks performed
        check_duration (Histogram): Duration of health checks
        check_failures (Counter): Count of failed health checks

    Example:
        ```python
        metrics = ConnectionHealthMetrics()
        metrics.health_score.labels(encoder_id='encoder_1', 
                                  connection_id='conn_123').set(95.5)
        metrics.health_checks.labels(encoder_id='encoder_1', 
                                   result='success').inc()
        ```
    """
    health_score = Gauge('helo_connection_health', 
                        'Connection health score', 
                        ['encoder_id', 'connection_id'])
    health_checks = Counter('helo_health_checks_total', 
                          'Number of health checks', 
                          ['encoder_id', 'result'])

class ConnectionHealthChecker:
    """
    Enhanced health checking system for HELO connections.
    
    Integrates with AJA REST API client and database models to provide
    comprehensive health monitoring for HELO encoders.
    """
    
    def __init__(self, 
                 thermal_manager: ConnectionThermalManager,
                 db_session=None,
                 redis_client=None):
        self.thermal_manager = thermal_manager
        self.health_metrics = ConnectionHealthMetrics()
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Enhanced health checks dictionary
        self.health_checks = {
            'basic_connectivity': self._check_basic_connectivity,
            'response_time': self._check_response_time,
            'error_rate': self._check_error_rate,
            'thermal_status': self._check_thermal_status,
            'resource_usage': self._check_resource_usage,
            'streaming_state': self._check_streaming_state,
            'recording_state': self._check_recording_state
        }

    async def _check_streaming_state(self, 
                                   encoder_id: str, 
                                   connection_id: str) -> Dict:
        """
        Check encoder streaming state using AJA's REST API.
        
        Args:
            encoder_id (str): The encoder ID to check
            connection_id (str): The connection ID to check
            
        Returns:
            Dict: Streaming state check results
        """
        try:
            encoder = HeloEncoder.query.get(encoder_id)
            device = AJADevice(f"http://{encoder.ip_address}")
            
            streaming_state = await device.get_param("eParamID_ReplicatorStreamState")
            
            return {
                'status': 'ok' if streaming_state["value"] == 2 else 'warning',
                'streaming_active': streaming_state["value"] == 2,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _check_recording_state(self, 
                                   encoder_id: str, 
                                   connection_id: str) -> Dict:
        """
        Check encoder recording state using AJA's REST API.
        
        Args:
            encoder_id (str): The encoder ID to check
            connection_id (str): The connection ID to check
            
        Returns:
            Dict: Recording state check results
        """
        try:
            encoder = HeloEncoder.query.get(encoder_id)
            device = AJADevice(f"http://{encoder.ip_address}")
            
            recording_state = await device.get_param("eParamID_ReplicatorRecordState")
            
            return {
                'status': 'ok' if recording_state["value"] == 2 else 'warning',
                'recording_active': recording_state["value"] == 2,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def get_detailed_health(self, encoder_id: str) -> Dict:
        """
        Get detailed health status for an encoder.
        
        Combines system health checks with encoder-specific checks.
        
        Args:
            encoder_id (str): The encoder ID to check
            
        Returns:
            Dict: Comprehensive health status
        """
        connection_id = await self.thermal_manager.get_active_connection(encoder_id)
        
        health_status = await self.perform_health_check(encoder_id, connection_id)
        
        # Add system-level checks
        if self.db_session:
            health_status['database'] = self._check_database()
        if self.redis_client:
            health_status['redis'] = self._check_redis()
            
        return health_status

    def _check_database(self) -> Dict:
        """Check database connectivity"""
        try:
            self.db_session.execute('SELECT 1')
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_redis(self) -> Dict:
        """Check Redis connectivity"""
        try:
            self.redis_client.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)} 
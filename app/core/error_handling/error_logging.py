from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging
from prometheus_client import Counter, Histogram
from app.core.enums import EncoderStatus, StreamingState, EventType
from app.core.security.security_logger import SecurityEventLogger
from app.core.error_handling.central_error_manager import HeloErrorType
from app.core.aja.aja_constants import ReplicatorCommands, MediaState, AJAParameters
from pathlib import Path

# This file contains multiple levels of abstraction for error handling and logging:
# 1. ErrorMetrics: Defines Prometheus metrics for tracking various error types and events.
# 2. ErrorLogger: Centralized error logging system that initializes loggers and handles different error types.
# 3. setup_loggers: Method within ErrorLogger to set up different log handlers for various error categories.
# 4. setup_logger: Method within ErrorLogger to configure individual loggers with enhanced formatting.
# 5. log_state_change: Method within ErrorLogger to log state changes for monitoring.
# 6. log_enhanced_error: Method within ErrorLogger to log detailed error context and update metrics.
# 
# The following areas are blank and require input from the user:
# - Additional methods for handling specific error types or logging requirements that are not yet defined.
# - Configuration details for log formatting and output destinations that may need customization.
# - Any additional metrics or logging categories that the user might want to track.



class ErrorMetrics:
    """Metrics for error tracking"""
    error_counter = Counter('error_total', 'Total errors by type and service', ['error_type', 'service'])
    error_severity = Counter('error_severity_total', 'Errors by severity level', ['severity'])
    error_resolution_time = Histogram('error_resolution_seconds', 'Time to resolve errors')
    helo_errors = Counter('helo_errors_total', 'HELO-specific errors', ['error_type', 'encoder_id'])
    security_events = Counter('security_events_total', 'Security-related events', ['event_type'])
    connection_failures = Counter('connection_failures_total', 'Connection failures', ['service'])

class ErrorLogger:
    """Centralized error logging system"""

    def __init__(self, app=None):
        self.app = app
        self.log_path = Path(app.config.get('LOG_PATH', 'logs'))
        self.metrics = ErrorMetrics()
        self.security_logger = SecurityEventLogger(app) if app else None
        self.setup_loggers()

    def setup_loggers(self):
        """Setup different log handlers"""
        self.loggers = {
            # API and Connection Errors
            'api': self.setup_logger('api', 'api.log'),
            'connection': self.setup_logger('connection', 'connection.log'),
            'pool': self.setup_logger('pool', 'pool.log'),
            
            # Encoder and Stream Errors
            'encoder': self.setup_logger('encoder', 'encoder.log'),
            'stream': self.setup_logger('stream', 'stream.log'),
            'helo': self.setup_logger('helo', 'helo.log'),
            
            # Security Errors
            'security': self.setup_logger('security', 'security.log'),
            'ssl': self.setup_logger('ssl', 'ssl.log'),
            'auth': self.setup_logger('auth', 'auth.log'),
            
            # System Errors
            'system': self.setup_logger('system', 'system.log'),
            'critical': self.setup_logger('critical', 'critical.log')
        }

    def setup_logger(self, name: str, filename: str) -> logging.Logger:
        """Setup individual logger with enhanced formatting"""
        logger = logging.getLogger(f'error_handling.{name}')
        logger.setLevel(logging.INFO)
        
        # Ensure log directory exists
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(self.log_path / filename)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s\n'
            'Error: %(message)s\n'
            'Details: %(details)s\n'
            'Service: %(service)s\n'
            'Endpoint: %(endpoint)s\n'
            'Resolution: %(resolution)s\n'
            '-' * 80 + '\n'
        ))
        
        logger.addHandler(handler)
        return logger

    def log_error(self, 
                 error_data: Dict[str, Any], 
                 error_type: str = 'api',
                 severity: str = 'error',
                 resolution: Optional[str] = None) -> None:
        """Enhanced error logging with metrics"""
        logger = self.loggers.get(error_type, self.loggers['system'])
        
        # Prepare error details
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_data': error_data,
            'service': error_data.get('service', 'unknown'),
            'endpoint': error_data.get('endpoint', 'unknown'),
            'details': error_data.get('error', 'No details provided'),
            'resolution': resolution or 'No resolution provided'
        }
        
        # Update metrics
        self.metrics.error_counter.labels(
            error_type=error_type,
            service=log_entry['service']
        ).inc()
        
        self.metrics.error_severity.labels(severity=severity).inc()
        
        # Log with appropriate severity
        if severity == 'critical':
            logger.critical(
                "A critical error occurred",
                extra={
                    'details': log_entry['details'],
                    'service': log_entry['service'],
                    'endpoint': log_entry['endpoint'],
                    'resolution': log_entry['resolution']
                }
            )
            self.loggers['critical'].critical(
                "A critical error occurred",
                extra={
                    'details': log_entry['details'],
                    'service': log_entry['service'],
                    'endpoint': log_entry['endpoint'],
                    'resolution': log_entry['resolution']
                }
            )
        elif severity == 'warning':
            logger.warning(
                "A warning occurred",
                extra={
                    'details': log_entry['details'],
                    'service': log_entry['service'],
                    'endpoint': log_entry['endpoint'],
                    'resolution': log_entry['resolution']
                }
            )
        else:
            logger.error(
                "An error occurred",
                extra={
                    'details': log_entry['details'],
                    'service': log_entry['service'],
                    'endpoint': log_entry['endpoint'],
                    'resolution': log_entry['resolution']
                }
            )

    def log_security_event(self, 
                         event_type: str, 
                         details: Dict[str, Any],
                         severity: str = 'warning') -> None:
        """Specialized security event logging"""
        self.log_error(
            error_data={
                'service': 'security',
                'event_type': event_type,
                **details
            },
            error_type='security',
            severity=severity
        )

    def log_connection_error(self,
                           service: str,
                           endpoint: str,
                           error: Union[Exception, str],
                           severity: str = 'error') -> None:
        """Specialized connection error logging"""
        self.log_error(
            error_data={
                'service': service,
                'endpoint': endpoint,
                'error': str(error)
            },
            error_type='connection',
            severity=severity
        )

    def log_encoder_error(self,
                         encoder_id: str,
                         error_type: str,
                         details: Dict[str, Any],
                         severity: str = 'error') -> None:
        """Specialized encoder error logging"""
        self.log_error(
            error_data={
                'service': 'encoder',
                'encoder_id': encoder_id,
                'error_type': error_type,
                **details
            },
            error_type='encoder',
            severity=severity
        )

    def log_helo_error(self,
                      error_type: HeloErrorType,
                      encoder_id: str,
                      details: Dict[str, Any],
                      severity: str = 'error') -> None:
        """Log HELO-specific errors"""
        self.metrics.helo_errors.labels(
            error_type=error_type.value,
            encoder_id=encoder_id
        ).inc()
        
        self.log_error(
            error_data={
                'service': 'helo',
                'encoder_id': encoder_id,
                'error_type': error_type.value,
                'streaming_state': details.get(AJAParameters.STREAMING_PROFILE),
                'media_state': details.get(AJAParameters.MEDIA_STATE),
                **details
            },
            error_type='helo',
            severity=severity
        )

    def log_security_violation(self,
                             event_type: str,
                             source_ip: str,
                             details: Dict[str, Any],
                             severity: str = 'critical') -> None:
        """Log security violations"""
        self.metrics.security_events.labels(event_type=event_type).inc()
        
        if self.security_logger:
            self.security_logger.log_event(event_type, details)
            
        self.log_error(
            error_data={
                'service': 'security',
                'event_type': event_type,
                'source_ip': source_ip,
                **details
            },
            error_type='security',
            severity=severity
        )

    def log_aja_error(self,
                     command_type: ReplicatorCommands,
                     device_id: str,
                     error: Exception,
                     media_state: Optional[MediaState] = None,
                     severity: str = 'error') -> None:
        """Log AJA device-specific errors"""
        self.log_error(
            error_data={
                'service': 'aja',
                'device_id': device_id,
                'command': command_type.value,
                'media_state': media_state.value if media_state else None,
                'error': str(error)
            },
            error_type='aja',
            severity=severity
        )

    def log_connection_failure(self,
                             service: str,
                             endpoint: str,
                             error: Union[Exception, str],
                             retry_count: int,
                             severity: str = 'error') -> None:
        """Log connection failures with retry information"""
        self.metrics.connection_failures.labels(service=service).inc()
        
        self.log_error(
            error_data={
                'service': service,
                'endpoint': endpoint,
                'error': str(error),
                'retry_count': retry_count,
                'retry_exhausted': retry_count >= self.app.config.get('MAX_RETRIES', 3)
            },
            error_type='connection',
            severity=severity
        )

    def log_state_change(self,
                        service: str,
                        entity_id: str,
                        old_state: Union[EncoderStatus, StreamingState],
                        new_state: Union[EncoderStatus, StreamingState],
                        details: Optional[Dict] = None) -> None:
        """Log state changes for monitoring"""
        self.log_error(
            error_data={
                'service': service,
                'entity_id': entity_id,
                'event_type': EventType.STATE_CHANGE.value,
                'old_state': old_state.value,
                'new_state': new_state.value,
                **(details or {})
            },
            error_type='state_change',
            severity='info'
        )


    def log_enhanced_error(self,
                          error_type: str,
                          service: str,
                          resolution_strategy: str,
                          resolution_time: float) -> None:
        """Log error with detailed context and update enhanced metrics"""
        logger = self.loggers.get('system')
        logger.error(
            f"Error occurred in service {service}",
            extra={
                'error_type': error_type,
                'service': service,
                'resolution_strategy': resolution_strategy,
                'resolution_time': resolution_time
            }
        )
        
        # Update metrics
        self.metrics.error_counter.labels(error_type=error_type, service=service).inc()
        self.metrics.error_resolution_time.labels(resolution_strategy=resolution_strategy).observe(resolution_time)


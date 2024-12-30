from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.error_handling.error_types import ErrorType
from app.core.error_handling.exceptions import EncoderError
from app.monitoring.error_analysis import ErrorAnalyzer
from app.services.performance_monitor import PerformanceMonitor

class HeloErrorTracker:
    """Tracks and analyzes HELO-specific errors"""
    
    def __init__(self, error_analyzer: ErrorAnalyzer, performance_monitor: PerformanceMonitor):
        self.error_analyzer = error_analyzer
        self.performance_monitor = performance_monitor
        self.error_history: Dict[str, List[Dict]] = defaultdict(list)
        self.recovery_attempts: Dict[str, Dict] = defaultdict(dict)
        self.consecutive_errors: Dict[str, int] = defaultdict(int)
        
        # Error thresholds for escalation
        self.thresholds = {
            'consecutive_errors': 3,
            'time_window': timedelta(minutes=5),
            'max_recovery_attempts': 5
        }

    async def track_error(self, encoder_id: str, error: Exception, context: Dict) -> Dict:
        """Track and analyze a HELO error"""
        error_entry = self._create_error_entry(encoder_id, error, context)
        
        # Store error in history
        self.error_history[encoder_id].append(error_entry)
        
        # Update consecutive error count
        if self._is_similar_to_last_error(encoder_id, error_entry):
            self.consecutive_errors[encoder_id] += 1
        else:
            self.consecutive_errors[encoder_id] = 1

        # Analyze error pattern
        analysis = await self._analyze_error_pattern(encoder_id, error_entry)
        
        # Track performance impact
        await self._track_performance_impact(encoder_id, error_entry)
        
        return {
            'error_entry': error_entry,
            'analysis': analysis,
            'consecutive_count': self.consecutive_errors[encoder_id],
            'requires_escalation': self._check_escalation_needed(encoder_id)
        }

    def _create_error_entry(self, encoder_id: str, error: Exception, context: Dict) -> Dict:
        """Create detailed error entry"""
        error_type = (
            error.details.get('error_type')
            if isinstance(error, EncoderError)
            else ErrorType.STREAM_CONFIG.value
        )
        
        error_code = "E001" if isinstance(error, EncoderError) else "E002"
        
        return {
            'timestamp': datetime.utcnow(),
            'encoder_id': encoder_id,
            'error_type': error_type,
            'error_code': error_code,
            'message': str(error),
            'context': context,
            'recovery_attempts': self.recovery_attempts[encoder_id].get(error_type, 0)
        }

    async def record_recovery_attempt(self, encoder_id: str, error_type: str, success: bool) -> Dict:
        """Record a recovery attempt"""
        current_attempts = self.recovery_attempts[encoder_id].get(error_type, 0)
        self.recovery_attempts[encoder_id][error_type] = current_attempts + 1
        
        if success:
            # Reset consecutive error count on successful recovery
            self.consecutive_errors[encoder_id] = 0
            
        return {
            'encoder_id': encoder_id,
            'error_type': error_type,
            'attempt_number': current_attempts + 1,
            'success': success,
            'timestamp': datetime.utcnow()
        }

    def _is_similar_to_last_error(self, encoder_id: str, current_error: Dict) -> bool:
        """Check if error is similar to the last one"""
        if not self.error_history[encoder_id]:
            return False
            
        last_error = self.error_history[encoder_id][-1]
        time_diff = current_error['timestamp'] - last_error['timestamp']
        
        return (
            last_error['error_type'] == current_error['error_type']
            and time_diff <= self.thresholds['time_window']
        )

    async def _analyze_error_pattern(self, encoder_id: str, error_entry: Dict) -> Dict:
        """Analyze error patterns using ErrorAnalyzer"""
        return await self.error_analyzer.analyze_error({
            'encoder_id': encoder_id,
            'type': error_entry['error_type'],
            'message': error_entry['message'],
            'context': error_entry['context']
        })

    async def _track_performance_impact(self, encoder_id: str, error_entry: Dict):
        """Track performance impact of errors"""
        self.performance_monitor.record_client_metrics(encoder_id, {
            'error_count': self.consecutive_errors[encoder_id],
            'recovery_attempts': sum(
                self.recovery_attempts[encoder_id].values()
            ),
            'last_error_type': error_entry['error_type']
        })

    def _check_escalation_needed(self, encoder_id: str) -> bool:
        """Check if error requires escalation"""
        return (
            self.consecutive_errors[encoder_id] >= self.thresholds['consecutive_errors']
            or any(
                attempts >= self.thresholds['max_recovery_attempts']
                for attempts in self.recovery_attempts[encoder_id].values()
            )
        )

    def get_error_history(self, encoder_id: str, 
                         time_window: Optional[timedelta] = None) -> List[Dict]:
        """Get error history for an encoder"""
        if not time_window:
            time_window = self.thresholds['time_window']
            
        cutoff_time = datetime.utcnow() - time_window
        return [
            error for error in self.error_history[encoder_id]
            if error['timestamp'] >= cutoff_time
        ] 
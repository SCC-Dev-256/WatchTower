from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.error_handling.errors.error_types import ErrorType
from app.core.error_handling.errors.exceptions import EncoderError
from app.core.error_handling import ErrorAnalyzer
from app.core.error_handling.performance_monitoring import PerformanceMonitor

# This file contains the HeloErrorTracker class, which is used to track and analyze HELO-specific errors.
# The HeloErrorTracker class uses an ErrorAnalyzer to analyze error patterns and a PerformanceMonitor to track performance impact.
# The HeloErrorTracker class has the following methods:
# - track_error: Tracks and analyzes a HELO error.
# - create_error_entry: Creates a detailed error entry.
# - record_recovery_attempt: Records a recovery attempt.
# - is_similar_to_last_error: Checks if the current error is similar to the last one.
# - analyze_error_pattern: Analyzes error patterns using ErrorAnalyzer.
# - track_performance_impact: Tracks the performance impact of errors.
# - check_escalation_needed: Checks if an error requires escalation.
# - get_error_history: Gets the error history for an encoder.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `track_error` method.
# - Detailed implementation for methods like `create_error_entry`, `record_recovery_attempt`, `is_similar_to_last_error`, `analyze_error_pattern`, `track_performance_impact`, and `check_escalation_needed`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `track_error` method.


class HeloErrorTracker:
    """
    A class to track and analyze HELO-specific errors.

    This class provides methods to log errors, analyze error patterns, track
    recovery attempts, and determine if an error requires escalation. It uses
    an ErrorAnalyzer to analyze error patterns and a PerformanceMonitor to
    track the performance impact of errors.
    """
    
    def __init__(self, error_analyzer: ErrorAnalyzer, performance_monitor: PerformanceMonitor):
        """
        Initialize the HeloErrorTracker with an error analyzer and a performance monitor.

        Args:
            error_analyzer (ErrorAnalyzer): An instance of ErrorAnalyzer to analyze error patterns.
            performance_monitor (PerformanceMonitor): An instance of PerformanceMonitor to track performance impact.
        """
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
        """
        Track and analyze a HELO error.

        Args:
            encoder_id (str): The ID of the encoder.
            error (Exception): The error to track.
            context (Dict): Additional context for the error.

        Returns:
            Dict: A dictionary containing the error entry, analysis, consecutive error count, and escalation requirement.
        """
        error_entry = self.create_error_entry(encoder_id, error, context)
        
        # Store error in history
        self.error_history[encoder_id].append(error_entry)
        
        # Update consecutive error count
        if self.is_similar_to_last_error(encoder_id, error_entry):
            self.consecutive_errors[encoder_id] += 1
        else:
            self.consecutive_errors[encoder_id] = 1

        # Analyze error pattern
        analysis = await self.analyze_error_pattern(encoder_id, error_entry)
        
        # Track performance impact
        await self.track_performance_impact(encoder_id, error_entry)
        
        return {
            'error_entry': error_entry,
            'analysis': analysis,
            'consecutive_count': self.consecutive_errors[encoder_id],
            'requires_escalation': self.check_escalation_needed(encoder_id)
        }

    def create_error_entry(self, encoder_id: str, error: Exception, context: Dict) -> Dict:
        """
        Create a detailed error entry.

        Args:
            encoder_id (str): The ID of the encoder.
            error (Exception): The error to create an entry for.
            context (Dict): Additional context for the error.

        Returns:
            Dict: A dictionary representing the error entry.
        """
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
        """
        Record a recovery attempt.

        Args:
            encoder_id (str): The ID of the encoder.
            error_type (str): The type of error being recovered from.
            success (bool): Whether the recovery attempt was successful.

        Returns:
            Dict: A dictionary containing details of the recovery attempt.
        """
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

    def is_similar_to_last_error(self, encoder_id: str, current_error: Dict) -> bool:
        """
        Check if the current error is similar to the last one.

        Args:
            encoder_id (str): The ID of the encoder.
            current_error (Dict): The current error entry.

        Returns:
            bool: True if the current error is similar to the last one, False otherwise.
        """
        if not self.error_history[encoder_id]:
            return False
            
        last_error = self.error_history[encoder_id][-1]
        time_diff = current_error['timestamp'] - last_error['timestamp']
        
        return (
            last_error['error_type'] == current_error['error_type']
            and time_diff <= self.thresholds['time_window']
        )

    async def analyze_error_pattern(self, encoder_id: str, error_entry: Dict) -> Dict:
        """
        Analyze error patterns using ErrorAnalyzer.

        Args:
            encoder_id (str): The ID of the encoder.
            error_entry (Dict): The error entry to analyze.

        Returns:
            Dict: The result of the error analysis.
        """
        return await self.error_analyzer.analyze_error({
            'encoder_id': encoder_id,
            'type': error_entry['error_type'],
            'message': error_entry['message'],
            'context': error_entry['context']
        })

    async def track_performance_impact(self, encoder_id: str, error_entry: Dict):
        """
        Track the performance impact of errors.

        Args:
            encoder_id (str): The ID of the encoder.
            error_entry (Dict): The error entry to track.
        """
        self.performance_monitor.record_client_metrics(encoder_id, {
            'error_count': self.consecutive_errors[encoder_id],
            'recovery_attempts': sum(
                self.recovery_attempts[encoder_id].values()
            ),
            'last_error_type': error_entry['error_type']
        })

    def check_escalation_needed(self, encoder_id: str) -> bool:
        """
        Check if an error requires escalation.

        Args:
            encoder_id (str): The ID of the encoder.

        Returns:
            bool: True if escalation is needed, False otherwise.
        """
        return (
            self.consecutive_errors[encoder_id] >= self.thresholds['consecutive_errors']
            or any(
                attempts >= self.thresholds['max_recovery_attempts']
                for attempts in self.recovery_attempts[encoder_id].values()
            )
        )

    def get_error_history(self, encoder_id: str, 
                         time_window: Optional[timedelta] = None) -> List[Dict]:
        """
        Get the error history for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.
            time_window (Optional[timedelta], optional): The time window to filter errors. Defaults to None.

        Returns:
            List[Dict]: A list of error entries within the specified time window.
        """
        if not time_window:
            time_window = self.thresholds['time_window']
            
        cutoff_time = datetime.utcnow() - time_window
        return [
            error for error in self.error_history[encoder_id]
            if error['timestamp'] >= cutoff_time
        ] 
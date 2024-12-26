from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from app.core.error_handling.error_types import ErrorType

class ErrorCorrelationAnalyzer:
    """Advanced error correlation analysis"""
    
    def __init__(self):
        self.correlation_windows = {
            'short': timedelta(minutes=5),
            'medium': timedelta(minutes=30),
            'long': timedelta(hours=2)
        }
        self.correlation_patterns = defaultdict(list)
        self.error_sequences = defaultdict(list)

    async def analyze_correlations(self, error: Dict) -> Dict:
        """Analyze error correlations across multiple dimensions"""
        encoder_id = error.get('encoder_id')
        timestamp = error.get('timestamp')
        
        return {
            'temporal': await self._analyze_temporal_patterns(encoder_id, timestamp),
            'causal': await self._analyze_causal_relationships(error),
            'resource': await self._analyze_resource_correlations(error),
            'network': await self._analyze_network_correlations(error),
            'state': await self._analyze_state_correlations(error),
            'sequence': await self._analyze_error_sequences(encoder_id, error)
        }

    async def _analyze_temporal_patterns(self, encoder_id: str, timestamp: datetime) -> Dict:
        """Analyze temporal error patterns"""
        patterns = {}
        for window_name, window in self.correlation_windows.items():
            patterns[window_name] = {
                'error_count': await self._count_errors_in_window(encoder_id, timestamp, window),
                'error_types': await self._get_error_types_in_window(encoder_id, timestamp, window),
                'peak_times': await self._find_error_peak_times(encoder_id, timestamp, window)
            }
        return patterns

    async def _analyze_causal_relationships(self, error: Dict) -> Dict:
        """Analyze potential cause-effect relationships"""
        return {
            'triggers': await self._identify_error_triggers(error),
            'consequences': await self._predict_error_consequences(error),
            'chain_probability': await self._calculate_chain_probability(error)
        }

    async def _analyze_resource_correlations(self, error: Dict) -> Dict:
        """Analyze correlations with system resources"""
        return {
            'cpu': await self._correlate_with_cpu_metrics(error),
            'memory': await self._correlate_with_memory_metrics(error),
            'network': await self._correlate_with_network_metrics(error),
            'disk': await self._correlate_with_disk_metrics(error)
        } 
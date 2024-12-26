from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import re
from typing import Dict, List, Optional
from flask import current_app
from app.core.aja_remediation_service import AJARemediationService

class ErrorAnalyzer:
    def __init__(self, app):
        self.app = app
        self.error_patterns = app.config['AJA_ERROR_PATTERNS']
        self.error_history = defaultdict(list)
        self.correlation_window = timedelta(minutes=5)
        self.aja_remediation = AJARemediationService(app)
        
    def analyze_error(self, error: Dict) -> Dict:
        """Comprehensive error analysis"""
        analysis = {
            'pattern_match': self._match_error_pattern(error),
            'correlation': self._find_correlations(error),
            'impact_assessment': self._assess_impact(error),
            'root_cause': self._analyze_root_cause(error),
            'suggested_actions': self._suggest_actions(error),
            'historical_context': self._get_historical_context(error)
        }
        
        # Store error for future analysis
        self._store_error(error)
        return analysis
    
    def _match_error_pattern(self, error: Dict) -> Optional[Dict]:
        """Match error against known patterns"""
        error_msg = error.get('message', '')
        for pattern_name, pattern in self.error_patterns.items():
            if re.search(pattern['pattern'], error_msg):
                return {
                    'pattern_name': pattern_name,
                    'severity': pattern['severity'],
                    'category': pattern['category'],
                    'mitigation': pattern['mitigation']
                }
        return None
    
    def _find_correlations(self, error: Dict) -> List[Dict]:
        """Find correlated errors and events"""
        correlations = []
        error_time = datetime.fromisoformat(error['timestamp'])
        window_start = error_time - self.correlation_window
        
        # Check for related errors in time window
        for stored_error in self.error_history[error['encoder_id']]:
            if window_start <= stored_error['timestamp'] <= error_time:
                correlations.append({
                    'type': 'error',
                    'details': stored_error,
                    'time_diff': (error_time - stored_error['timestamp']).total_seconds()
                })
        
        # Check system metrics for anomalies
        metrics = self._get_metrics_in_window(error['encoder_id'], window_start, error_time)
        if metrics:
            correlations.extend(self._analyze_metrics_correlation(metrics))
            
        return correlations
    
    def _assess_impact(self, error: Dict) -> Dict:
        """Assess the impact of the error"""
        return {
            'service_impact': self._calculate_service_impact(error),
            'affected_users': self._get_affected_users(error),
            'downstream_effects': self._analyze_downstream_effects(error),
            'recovery_time_estimate': self._estimate_recovery_time(error)
        }
    
    def _analyze_state_transitions(self, error: Dict) -> Dict:
        """Analyze encoder state transitions leading to errors"""
        encoder_id = error['encoder_id']
        error_time = datetime.fromisoformat(error['timestamp'])
        window_start = error_time - timedelta(minutes=30)
        
        # Get state history
        states = self._get_encoder_states(encoder_id, window_start, error_time)
        transitions = self._calculate_state_transitions(states)
        
        return {
            'state_sequence': states,
            'critical_transitions': self._identify_critical_transitions(transitions),
            'stable_states': self._identify_stable_states(states),
            'risk_states': self._identify_risk_states(transitions)
        }
    
    def _analyze_resource_correlation(self, error: Dict) -> Dict:
        """Analyze correlation with system resources"""
        metrics = self._get_resource_metrics(error['encoder_id'])
        
        return {
            'cpu_correlation': self._correlate_with_cpu(metrics),
            'memory_correlation': self._correlate_with_memory(metrics),
            'network_correlation': self._correlate_with_network(metrics),
            'storage_correlation': self._correlate_with_storage(metrics)
        } 
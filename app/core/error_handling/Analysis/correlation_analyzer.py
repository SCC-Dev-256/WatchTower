from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict
from app.core.error_handling.errors.error_types import ErrorType
import requests
import matplotlib.pyplot as plt
from app.core.config.parameter_config import ParameterConfig
from app.core.aja.machine_logic.helo_params import HeloParameters

class ErrorAnalyzer:
    """Advanced error correlation analysis"""
    
    def __init__(self, app=None):
        self.app = app
        self.parameter_config = ParameterConfig()
        self.error_patterns = app.config.get('ERROR_PATTERNS', {}) if app else {}
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
        
        # Fetch logs and metrics
        logs = self._fetch_logs(encoder_id)
        metrics = self._fetch_metrics(encoder_id)
        
        # Merge basic error analysis from ErrorAnalyzer
        basic_analysis = {
            'pattern_match': self._match_error_pattern(error),
            'suggested_actions': self._get_suggested_actions(error),
            'severity': self._determine_severity(error)
        }
        
        # Add advanced correlation analysis
        return {
            **basic_analysis,
            'temporal': await self._analyze_temporal_patterns(encoder_id, timestamp, logs),
            'causal': await self._analyze_causal_relationships(error),
            'resource': await self._analyze_resource_correlations(metrics),
            'network': await self._analyze_network_correlations(error),
            'state': await self._analyze_state_correlations(error),
            'sequence': await self._analyze_error_sequences(encoder_id, error)
        }

    def _fetch_logs(self, encoder_id: str) -> pd.DataFrame:
        """Fetch logs from AJA HELO REST API"""
        # Example API call to fetch logs
        response = requests.get(f"http://api.example.com/encoders/{encoder_id}/logs")
        log_data = response.json()
        logs = pd.DataFrame(log_data)
        logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        return logs

    def _fetch_metrics(self, encoder_id: str) -> pd.DataFrame:
        """Fetch resource metrics from monitoring tools"""
        # Example API call to fetch metrics
        response = requests.get(f"http://api.example.com/encoders/{encoder_id}/metrics")
        metric_data = response.json()
        metrics = pd.DataFrame(metric_data)
        return metrics

    def _match_error_pattern(self, error_data: Dict) -> Optional[Dict]:
        """Match error against known patterns"""
        error_type = error_data.get('type')
        if error_type in self.error_patterns:
            return self.error_patterns[error_type]
        return None

    def _get_suggested_actions(self, error_data: Dict) -> list:
        """Get suggested remediation actions"""
        pattern = self._match_error_pattern(error_data)
        return pattern.get('actions', []) if pattern else []

    def _determine_severity(self, error_data: Dict) -> str:
        """Determine error severity"""
        pattern = self._match_error_pattern(error_data)
        return pattern.get('severity', 'error') if pattern else 'error'

    async def _analyze_temporal_patterns(self, encoder_id: str, timestamp: datetime, logs: pd.DataFrame) -> Dict:
        """Analyze temporal error patterns"""
        patterns = {}
        for window_name, window in self.correlation_windows.items():
            patterns[window_name] = {
                'error_count': await self._count_errors_in_window(encoder_id, timestamp, window, logs),
                'error_types': await self._get_error_types_in_window(encoder_id, timestamp, window, logs),
                'peak_times': await self._find_error_peak_times(encoder_id, timestamp, window, logs)
            }
        return patterns

    async def _analyze_causal_relationships(self, error: Dict) -> Dict:
        """Analyze potential cause-effect relationships"""
        return {
            'triggers': await self._identify_error_triggers(error),
            'consequences': await self._predict_error_consequences(error),
            'chain_probability': await self._calculate_chain_probability(error)
        }

    async def _analyze_resource_correlations(self, metrics: pd.DataFrame) -> Dict:
        """Analyze correlations with system resources"""
        return {
            'cpu': await self._correlate_with_cpu_metrics(metrics),
            'memory': await self._correlate_with_memory_metrics(metrics),
            'network': await self._correlate_with_network_metrics(metrics),
            'disk': await self._correlate_with_disk_metrics(metrics)
        }

    # Visualization (optional, using matplotlib)
    def visualize_resource_usage(self, logs: pd.DataFrame):
        plt.plot(logs['timestamp'], logs['cpu_usage'], label="CPU Usage")
        plt.plot(logs['timestamp'], logs['memory_usage'], label="Memory Usage")
        plt.legend()
        plt.title("Resource Usage Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Usage (%)")
        plt.show()

    def use_parameters_for_analysis(self, helo_params: HeloParameters) -> Dict:
        """Analyze error correlations based on HELO device parameters"""
        analysis_data = {
            'network_params': {
                'ip_config': {
                    'type': helo_params.ip_address_type,
                    'address': helo_params.ip_address,
                    'subnet': helo_params.subnet_mask,
                    'gateway': helo_params.default_gateway
                },
                'connection_state': {
                    'connected': helo_params.network_connected,
                    'link_state': helo_params.link_state,
                    'error_count': helo_params.network_link_error_count
                }
            },
            'error_behaviors': {
                'dropped_frames': {
                    'record': helo_params.dropped_frames_record_behavior,
                    'stream': helo_params.dropped_frames_stream_behavior
                },
                'video_loss': helo_params.loss_of_video_behavior,
                'auto_recover': helo_params.auto_recover_streaming
            },
            'stream_config': {
                'format': helo_params.streaming_format,
                'url': helo_params.stream_url,
                'duration': helo_params.streaming_duration
            }
        }

        # TODO: Once database is set up, correlate these parameters with error patterns
        # Suggested schema:
        # - error_events table: timestamp, error_type, severity, device_id
        # - device_params table: device_id, param_name, param_value, timestamp
        # - error_correlations table: error_id, param_id, correlation_strength

        return analysis_data


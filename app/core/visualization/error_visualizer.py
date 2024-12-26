from typing import Dict, List, Optional
import plotly.graph_objects as go
from app.core.error_handling.enhanced_metrics import EnhancedErrorMetrics

class ErrorVisualizer:
    """Base error visualization capabilities"""
    
    def __init__(self, metrics: EnhancedErrorMetrics):
        self.metrics = metrics

    async def create_error_timeline(self, encoder_id: str, time_range: str) -> Dict:
        """Create timeline visualization of errors"""
        timeline_data = await self.metrics.get_error_timeline(encoder_id, time_range)
        
        fig = go.Figure(data=[go.Scatter(
            x=timeline_data['timestamps'],
            y=timeline_data['error_counts'],
            mode='lines+markers'
        )])
        
        return fig.to_dict()

    async def create_error_distribution(self, encoder_id: str, time_range: str) -> Dict:
        """Create error distribution visualization"""
        distribution_data = await self.metrics.get_error_distribution(encoder_id, time_range)
        
        fig = go.Figure(data=[go.Bar(
            x=distribution_data['error_types'],
            y=distribution_data['counts']
        )])
        
        return fig.to_dict() 
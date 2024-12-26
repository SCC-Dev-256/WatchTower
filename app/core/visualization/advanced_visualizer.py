from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime, timedelta
import pandas as pd
from app.core.error_handling.enhanced_metrics import EnhancedErrorMetrics

class AdvancedErrorVisualizer:
    """Advanced error visualization capabilities"""
    
    def __init__(self, metrics: EnhancedErrorMetrics):
        self.metrics = metrics

    async def create_error_network(self, encoder_id: str, time_range: str) -> Dict:
        """Create network graph of error relationships"""
        error_data = await self.metrics.get_error_relationships(encoder_id, time_range)
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes and edges
        for error in error_data:
            G.add_node(error['id'], **error['attributes'])
            for related in error['related']:
                G.add_edge(error['id'], related['id'], 
                          weight=related['correlation_strength'])
        
        # Convert to plotly figure
        pos = nx.spring_layout(G)
        
        fig = go.Figure()
        
        # Add edges
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'))
        
        # Add nodes
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlOrRd',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        ))
        
        return fig.to_dict()

    async def create_error_sunburst(self, encoder_id: str, time_range: str) -> Dict:
        """Create sunburst chart of error hierarchy"""
        error_hierarchy = await self.metrics.get_error_hierarchy(encoder_id, time_range)
        
        fig = px.sunburst(
            error_hierarchy,
            path=['category', 'type', 'subtype'],
            values='count',
            color='severity',
            color_continuous_scale='RdYlBu'
        )
        
        return fig.to_dict()

    async def create_error_sankey(self, encoder_id: str, time_range: str) -> Dict:
        """Create Sankey diagram of error flows"""
        flow_data = await self.metrics.get_error_flows(encoder_id, time_range)
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=flow_data['nodes'],
                color="blue"
            ),
            link=dict(
                source=flow_data['source'],
                target=flow_data['target'],
                value=flow_data['value']
            )
        )])
        
        return fig.to_dict()

    async def create_3d_error_scatter(self, encoder_id: str, time_range: str) -> Dict:
        """Create 3D scatter plot of errors"""
        error_metrics = await self.metrics.get_error_metrics_3d(encoder_id, time_range)
        
        fig = go.Figure(data=[go.Scatter3d(
            x=error_metrics['severity'],
            y=error_metrics['frequency'],
            z=error_metrics['impact'],
            mode='markers',
            marker=dict(
                size=12,
                color=error_metrics['resolution_time'],
                colorscale='Viridis',
                opacity=0.8
            ),
            text=error_metrics['error_types']
        )])
        
        return fig.to_dict() 
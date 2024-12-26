"""Add metrics indexes

Revision ID: 003
Revises: 002
Create Date: 2024-03-20 12:00:00.000000
"""
from alembic import op

def upgrade():
    # Add indexes for common queries
    op.create_index('idx_metrics_timestamp', 'encoder_metrics', ['timestamp'])
    op.create_index('idx_metrics_encoder_timestamp', 
                    'encoder_metrics', 
                    ['encoder_id', 'timestamp'])
    op.create_index('idx_alerts_timestamp', 'alert', ['timestamp'])
    op.create_index('idx_alerts_encoder_timestamp', 
                    'alert', 
                    ['encoder_id', 'timestamp'])
    op.create_index('idx_alerts_type', 'alert', ['type'])
    op.create_index('idx_alerts_severity', 'alert', ['severity'])

def downgrade():
    op.drop_index('idx_metrics_timestamp')
    op.drop_index('idx_metrics_encoder_timestamp')
    op.drop_index('idx_alerts_timestamp')
    op.drop_index('idx_alerts_encoder_timestamp')
    op.drop_index('idx_alerts_type')
    op.drop_index('idx_alerts_severity') 
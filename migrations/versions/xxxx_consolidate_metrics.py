"""Consolidate metrics tables

Revision ID: xxxx
Revises: yyyy
Create Date: 2024-01-20
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create new consolidated metrics table
    op.create_table(
        'encoder_metrics_v2',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encoder_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('streaming_data', sa.JSON(), nullable=True),
        sa.Column('bandwidth', sa.Integer(), nullable=True),
        sa.Column('storage_used', sa.BigInteger(), nullable=True),
        sa.Column('storage_total', sa.BigInteger(), nullable=True),
        sa.Column('storage_health', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['encoder_id'], ['encoder.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data from old tables
    op.execute("""
        INSERT INTO encoder_metrics_v2 (encoder_id, timestamp, streaming_data, 
                                      bandwidth, storage_used, storage_total)
        SELECT encoder_id, timestamp, streaming_data, bandwidth, 
               storage_used, storage_total
        FROM encoder_metrics
    """)
    
    # Drop old tables
    op.drop_table('encoder_metrics')
    op.drop_table('encoder_health_metrics')

def downgrade():
    # Reverse the migration if needed
    pass 
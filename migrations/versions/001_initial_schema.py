"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-03-21 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create enum type for encoder status
    op.execute("CREATE TYPE encoder_status AS ENUM ('offline', 'online', 'error', 'maintenance', 'unknown')")
    
    # Create encoders table
    op.create_table(
        'encoders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('ip_address', sa.String(15), nullable=False),
        sa.Column('status', sa.Enum('offline', 'online', 'error', 'maintenance', 'unknown', name='encoder_status'), server_default='unknown'),
        sa.Column('streaming_state', sa.Boolean(), server_default='false'),
        sa.Column('recording_state', sa.Boolean(), server_default='false'),
        sa.Column('last_checked', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('firmware_version', sa.String(50)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ip_address')
    )
    
    # Create encoder_metrics table
    op.create_table(
        'encoder_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encoder_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('cpu_usage', sa.Float()),
        sa.Column('memory_usage', sa.Float()),
        sa.Column('bandwidth_usage', sa.Float()),
        sa.Column('stream_health', sa.Float()),
        sa.Column('bitrate', sa.Integer()),
        sa.Column('frame_drops', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['encoder_id'], ['encoders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create encoder_configs table
    op.create_table(
        'encoder_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encoder_id', sa.Integer(), nullable=False),
        sa.Column('stream_url', sa.String(200)),
        sa.Column('stream_key', sa.String(100)),
        sa.Column('video_bitrate', sa.Integer()),
        sa.Column('audio_bitrate', sa.Integer()),
        sa.Column('resolution', sa.String(20)),
        sa.Column('fps', sa.Integer()),
        sa.Column('recording_format', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['encoder_id'], ['encoders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create encoder_events table
    op.create_table(
        'encoder_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encoder_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('event_type', sa.String(50)),
        sa.Column('description', sa.String(255)),
        sa.Column('severity', sa.String(20)),
        sa.ForeignKeyConstraint(['encoder_id'], ['encoders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('encoder_events')
    op.drop_table('encoder_configs')
    op.drop_table('encoder_metrics')
    op.drop_table('encoders')
    op.execute('DROP TYPE encoder_status') 
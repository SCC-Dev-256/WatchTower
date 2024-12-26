"""Add encoder configuration

Revision ID: 002
Revises: 001
Create Date: 2024-03-20 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add encoder configuration table
    op.create_table(
        'encoder_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encoder_id', sa.Integer(), nullable=False),
        sa.Column('stream_url', sa.String(200)),
        sa.Column('stream_key', sa.String(100)),
        sa.Column('video_bitrate', sa.Integer()),
        sa.Column('audio_bitrate', sa.Integer()),
        sa.Column('resolution', sa.String(20)),
        sa.Column('fps', sa.Integer()),
        sa.Column('recording_format', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['encoder_id'], ['encoder.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('encoder_config') 
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('helo_encoders', sa.Column('transcription_active', sa.Boolean(), default=False))
    op.add_column('helo_encoders', sa.Column('last_transcription_error', sa.String()))
    op.add_column('helo_encoders', sa.Column('transcription_start_time', sa.DateTime()))

def downgrade():
    op.drop_column('helo_encoders', 'transcription_active')
    op.drop_column('helo_encoders', 'last_transcription_error')
    op.drop_column('helo_encoders', 'transcription_start_time')

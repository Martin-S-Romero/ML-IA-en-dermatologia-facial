"""add password_reset_tokens table

Revision ID: c4d5e6f7a8b9
Revises: a3f9e2c1b8d7
Create Date: 2026-06-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision      = 'c4d5e6f7a8b9'
down_revision = 'a3f9e2c1b8d7'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.create_table(
        'password_reset_tokens',
        sa.Column('id',         sa.Integer(),                  nullable=False),
        sa.Column('user_id',    sa.Integer(),                  nullable=False),
        sa.Column('token',      sa.String(length=64),          nullable=False),
        sa.Column('used',       sa.Boolean(),                  nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True),    nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),    server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            name=op.f('fk_password_reset_tokens_user_id_users'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_password_reset_tokens')),
    )
    op.create_index(op.f('ix_password_reset_tokens_id'),      'password_reset_tokens', ['id'],      unique=False)
    op.create_index(op.f('ix_password_reset_tokens_token'),   'password_reset_tokens', ['token'],   unique=True)
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_token'),   table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_id'),      table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

"""add new fields: consents, analysis columns, birth_date, routine updated_at, products

Revision ID: a3f9e2c1b8d7
Revises: 9a61d17817dd
Create Date: 2026-05-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision      = 'a3f9e2c1b8d7'
down_revision = '9a61d17817dd'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    # ── consents ──────────────────────────────────────────────────────────────
    op.create_table(
        'consents',
        sa.Column('id',              sa.Integer(),               nullable=False),
        sa.Column('user_id',         sa.Integer(),               nullable=False),
        sa.Column('gdpr_accepted',   sa.Boolean(),               nullable=False),
        sa.Column('data_processing', sa.Boolean(),               nullable=False),
        sa.Column('image_storage',   sa.Boolean(),               nullable=False),
        sa.Column('ai_analysis',     sa.Boolean(),               nullable=False),
        sa.Column('ip_address',      sa.String(length=45),       nullable=True),
        sa.Column('accepted_at',     sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            name=op.f('fk_consents_user_id_users'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_consents')),
    )
    op.create_index(op.f('ix_consents_id'),      'consents', ['id'],      unique=False)
    op.create_index(op.f('ix_consents_user_id'), 'consents', ['user_id'], unique=False)

    # ── users: updated_at ──────────────────────────────────────────────────────
    op.add_column(
        'users',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # ── skin_profiles: age → birth_date ───────────────────────────────────────
    op.add_column('skin_profiles', sa.Column('birth_date', sa.Date(), nullable=True))
    op.drop_column('skin_profiles', 'age')

    # ── analyses: new columns ─────────────────────────────────────────────────
    op.add_column('analyses', sa.Column('face_censored',   sa.Boolean(),      nullable=False, server_default='false'))
    op.add_column('analyses', sa.Column('lighting',        sa.String(50),     nullable=True))
    op.add_column('analyses', sa.Column('device',          sa.String(255),    nullable=True))
    op.add_column('analyses', sa.Column('top1_label',      sa.String(50),     nullable=True))
    op.add_column('analyses', sa.Column('top1_confidence', sa.Float(),        nullable=True))
    op.add_column('analyses', sa.Column('model_version',   sa.String(50),     nullable=True))
    # original_filename: make nullable (GDPR delete)
    op.alter_column('analyses', 'original_filename', nullable=True)

    # ── routines: updated_at ───────────────────────────────────────────────────
    op.add_column(
        'routines',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # ── routine_steps: new columns ────────────────────────────────────────────
    op.add_column('routine_steps', sa.Column('product_id',    sa.Integer(), nullable=True))
    op.add_column('routine_steps', sa.Column('ai_suggested',  sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('routine_steps', sa.Column('user_replaced', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('routine_steps', sa.Column('replaced_with', sa.String(length=255), nullable=True))
    op.create_foreign_key(
        'fk_routine_steps_product_id_products',
        'routine_steps', 'products',
        ['product_id'], ['id'],
        ondelete='SET NULL',
    )

    # ── products: new columns ─────────────────────────────────────────────────
    op.add_column('products', sa.Column(
        'suitable_for',   postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('products', sa.Column(
        'last_scraped_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # products
    op.drop_column('products', 'last_scraped_at')
    op.drop_column('products', 'suitable_for')

    # routine_steps
    op.drop_constraint('fk_routine_steps_product_id_products', 'routine_steps', type_='foreignkey')
    op.drop_column('routine_steps', 'replaced_with')
    op.drop_column('routine_steps', 'user_replaced')
    op.drop_column('routine_steps', 'ai_suggested')
    op.drop_column('routine_steps', 'product_id')

    # routines
    op.drop_column('routines', 'updated_at')

    # analyses
    op.alter_column('analyses', 'original_filename', nullable=False)
    op.drop_column('analyses', 'model_version')
    op.drop_column('analyses', 'top1_confidence')
    op.drop_column('analyses', 'top1_label')
    op.drop_column('analyses', 'device')
    op.drop_column('analyses', 'lighting')
    op.drop_column('analyses', 'face_censored')

    # skin_profiles
    op.add_column('skin_profiles', sa.Column('age', sa.Integer(), nullable=True))
    op.drop_column('skin_profiles', 'birth_date')

    # users
    op.drop_column('users', 'updated_at')

    # consents
    op.drop_index(op.f('ix_consents_user_id'), table_name='consents')
    op.drop_index(op.f('ix_consents_id'),      table_name='consents')
    op.drop_table('consents')

"""initial_schema

Revision ID: 20260328_initial_schema
Revises: 
Create Date: 2026-03-28
"""

from alembic import op


revision = "20260328_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')


def downgrade() -> None:
    pass

"""removed index from all tables with primary key

Revision ID: 61d55eab0cbb
Revises: 894fe3afffb3
Create Date: 2026-07-30 14:46:51.155823
"""

from alembic import op
import sqlalchemy as sa

revision = "61d55eab0cbb"
down_revision = "894fe3afffb3"
branch_labels = None
depends_on = None


def upgrade():
    # Primary keys are already indexed by PostgreSQL.
    # No migration is required.
    pass


def downgrade():
    # Nothing to undo.
    pass
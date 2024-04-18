"""switch question.next to json blob

Revision ID: 7f024829d45e
Revises: 9c972e807bd8
Create Date: 2024-04-18 15:02:33.305786

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7f024829d45e"
down_revision = "9c972e807bd8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE question SET next = '{}' WHERE next IS NOT NULL")

    # Step 2: Alter the column type to JSONB using raw SQL
    op.execute(
        """
        ALTER TABLE question
        ALTER COLUMN next TYPE JSONB
        USING next::JSONB
    """
    )


def downgrade():
    # Step 1: Revert the column type back to Text
    op.execute(
        """
        ALTER TABLE question
        ALTER COLUMN next TYPE TEXT
        USING next::TEXT
    """
    )

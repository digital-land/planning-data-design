"""add tags model

Revision ID: b1c0f99b3888
Revises: 145a88e26dd2
Create Date: 2024-12-10 10:55:58.622333

"""

import sqlalchemy as sa
from alembic import op
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision = "b1c0f99b3888"
down_revision = "145a88e26dd2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tag",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "consideration_tags",
        sa.Column("consideration_id", sa.UUID(), nullable=True),
        sa.Column("tag_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["consideration_id"],
            ["consideration.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
    )
    # Create initial tags and tag any existing considerations
    from uuid import uuid4

    from sqlalchemy import String, text
    from sqlalchemy.sql import column, table

    # Define tables for raw SQL operations
    tag = table("tag", column("id", String), column("name", String))

    consideration_tags = table(
        "consideration_tags",
        column("consideration_id", String),
        column("tag_id", String),
    )

    # Create the initial tags
    llc_tag_id = str(uuid4())
    lp_tag_id = str(uuid4())

    op.bulk_insert(
        tag,
        [
            {
                "id": llc_tag_id,
                "name": "Local land charge",
            },
            {"id": lp_tag_id, "name": "Local plan"},
        ],
    )

    # Get all considerations with LLC or LP flags
    considerations = (
        op.get_bind()
        .execute(
            text(
                "SELECT id, is_local_land_charge, is_local_plan_data FROM consideration"
            )
        )
        .fetchall()
    )

    # Add tags to considerations
    for consideration in considerations:
        if consideration.is_local_land_charge:
            op.execute(
                consideration_tags.insert().values(
                    consideration_id=consideration.id, tag_id=llc_tag_id
                )
            )
        if consideration.is_local_plan_data:
            op.execute(
                consideration_tags.insert().values(
                    consideration_id=consideration.id, tag_id=lp_tag_id
                )
            )


# ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("consideration_tags")
    op.drop_table("tag")
    # ### end Alembic commands ###

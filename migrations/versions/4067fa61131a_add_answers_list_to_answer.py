"""add answers list to answer

Revision ID: 4067fa61131a
Revises: 1aa03adb00c0
Create Date: 2024-04-23 14:02:46.812094

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4067fa61131a'
down_revision = '1aa03adb00c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('answer_list', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.alter_column('answer',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('answer',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=False)
        batch_op.drop_column('answer_list')

    # ### end Alembic commands ###

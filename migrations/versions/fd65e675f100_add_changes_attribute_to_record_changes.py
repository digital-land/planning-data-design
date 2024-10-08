"""add changes attribute to record changes

Revision ID: fd65e675f100
Revises: 38f1ae6961f0
Create Date: 2024-03-25 15:10:19.961854

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fd65e675f100'
down_revision = '38f1ae6961f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consideration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consideration', schema=None) as batch_op:
        batch_op.drop_column('changes')

    # ### end Alembic commands ###

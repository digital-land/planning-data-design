"""add unique constraint to consideration name

Revision ID: 7f77e257eda9
Revises: f5f983060c64
Create Date: 2024-03-19 13:26:44.601852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f77e257eda9'
down_revision = 'f5f983060c64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consideration', schema=None) as batch_op:
        batch_op.create_unique_constraint('consideration_name_ak', ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consideration', schema=None) as batch_op:
        batch_op.drop_constraint('consideration_name_ak', type_="unique")

    # ### end Alembic commands ###
"""answer text to json

Revision ID: 1aa03adb00c0
Revises: 36380da0dc7b
Create Date: 2024-04-23 10:02:13.964742

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1aa03adb00c0'
down_revision = '36380da0dc7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('answer', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
        batch_op.drop_column('text')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.drop_column('answer')

    # ### end Alembic commands ###

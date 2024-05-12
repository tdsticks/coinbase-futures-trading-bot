"""

Revision ID: 5d5fccb3092d
Revises: 46551c4adfa3
Create Date: 2024-05-10 20:10:01.604262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d5fccb3092d'
down_revision = '46551c4adfa3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_authenticated', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('is_superuser', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_superuser')
        batch_op.drop_column('is_authenticated')

    # ### end Alembic commands ###

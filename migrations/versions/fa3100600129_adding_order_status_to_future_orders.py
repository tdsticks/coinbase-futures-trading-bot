"""Adding order status to Future Orders

Revision ID: fa3100600129
Revises: 5b602f1558a0
Create Date: 2024-04-24 08:34:45.265714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa3100600129'
down_revision = '5b602f1558a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('futures_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_status', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('futures_order', schema=None) as batch_op:
        batch_op.drop_column('order_status')

    # ### end Alembic commands ###
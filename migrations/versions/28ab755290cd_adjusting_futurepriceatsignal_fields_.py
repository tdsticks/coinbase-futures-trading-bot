"""Adjusting FuturePriceAtSignal fields for spot and future prices

Revision ID: 28ab755290cd
Revises: 738911d296f0
Create Date: 2024-04-16 22:25:14.158335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28ab755290cd'
down_revision = '738911d296f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('future_price_at_signal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('signal_spot_price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('future_bid_price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('future_ask_price', sa.Float(), nullable=True))
        batch_op.drop_column('ask_price')
        batch_op.drop_column('bid_price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('future_price_at_signal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bid_price', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('ask_price', sa.FLOAT(), nullable=True))
        batch_op.drop_column('future_ask_price')
        batch_op.drop_column('future_bid_price')
        batch_op.drop_column('signal_spot_price')

    # ### end Alembic commands ###
"""Adding more fields from the List Orders call to Future Orders

Revision ID: 9b69f5d61596
Revises: 95b675ef4015
Create Date: 2024-04-24 10:27:40.388637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b69f5d61596'
down_revision = '95b675ef4015'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('futures_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_type', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('time_in_force', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('order_placement_source', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('size_in_quote', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('size_inclusive_of_fees', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('fee', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('outstanding_hold_amount', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('settled', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('edit_history', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('cancel_message', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('pending_cancel', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('reject_message', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('reject_reason', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('created_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('futures_order', schema=None) as batch_op:
        batch_op.drop_column('created_time')
        batch_op.drop_column('reject_reason')
        batch_op.drop_column('reject_message')
        batch_op.drop_column('pending_cancel')
        batch_op.drop_column('cancel_message')
        batch_op.drop_column('edit_history')
        batch_op.drop_column('settled')
        batch_op.drop_column('outstanding_hold_amount')
        batch_op.drop_column('fee')
        batch_op.drop_column('size_inclusive_of_fees')
        batch_op.drop_column('size_in_quote')
        batch_op.drop_column('order_placement_source')
        batch_op.drop_column('time_in_force')
        batch_op.drop_column('product_type')

    # ### end Alembic commands ###
"""try to add table operation_type

Revision ID: 911f3d8b3e0a
Revises: b005af722aab
Create Date: 2023-04-16 10:58:59.965757

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '911f3d8b3e0a'
down_revision = 'b005af722aab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operation_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('operation_type_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('exchange_rates')
    op.add_column('instument', sa.Column('operation_type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'instument', 'operation_type', ['operation_type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'instument', type_='foreignkey')
    op.drop_column('instument', 'operation_type_id')
    op.create_table('exchange_rates',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('currency_pair', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('rate', sa.NUMERIC(precision=10, scale=4), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='exchange_rates_pkey')
    )
    op.drop_table('operation_type')
    # ### end Alembic commands ###
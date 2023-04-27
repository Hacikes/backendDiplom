"""default DB1

Revision ID: 605a61e4606d
Revises: ada9eb3e55b7
Create Date: 2023-04-27 21:33:39.977043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '605a61e4606d'
down_revision = 'ada9eb3e55b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('carrency_name', sa.String(), nullable=False),
    sa.Column('rate', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instrument_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_type_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('operation_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('operation_type_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('permissions', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('registered_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_name', sa.String(), nullable=False),
    sa.Column('broker_name', sa.String(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instrument',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('currency_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('figi', sa.String(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('instrument_type_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('operation_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['currency_id'], ['currency_type.id'], ),
    sa.ForeignKeyConstraint(['instrument_type_id'], ['instrument_type.id'], ),
    sa.ForeignKeyConstraint(['operation_type_id'], ['operation_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('total_quantity_and_avg_price_instrument_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_name', sa.String(), nullable=False),
    sa.Column('total_quantity', sa.Integer(), nullable=False),
    sa.Column('avg_price', sa.Float(), nullable=False),
    sa.Column('currency_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('instrument_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('total_quantity_and_avg_price_instrument_account')
    op.drop_table('instrument')
    op.drop_table('account')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('operation_type')
    op.drop_table('instrument_type')
    op.drop_table('currency_type')
    # ### end Alembic commands ###

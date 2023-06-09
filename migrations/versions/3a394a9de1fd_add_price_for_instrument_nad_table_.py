"""add price for instrument nad table currency_type

Revision ID: 3a394a9de1fd
Revises: ba8c55fd5353
Create Date: 2023-04-16 00:12:22.408118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a394a9de1fd'
down_revision = 'ba8c55fd5353'
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
    op.create_table('instument_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instument_type_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instument',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('currency_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('figi', sa.String(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('instument_type_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['currency_id'], ['currency_type.id'], ),
    sa.ForeignKeyConstraint(['instument_type_id'], ['instument_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('instument')
    op.drop_table('instument_type')
    op.drop_table('currency_type')
    # ### end Alembic commands ###

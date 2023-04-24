"""change instument on instrument

Revision ID: 50cd8ebfa262
Revises: fad0f32e08c7
Create Date: 2023-04-16 15:38:53.805091

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '50cd8ebfa262'
down_revision = 'fad0f32e08c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instrument_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_type_name', sa.String(), nullable=False),
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
    op.drop_table('instument')
    op.drop_table('instument_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instument_type',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('instument_type_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('instument_type_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='instument_type_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('instument',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('instrument_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('currency_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('figi', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('instument_type_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('operation_type_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name='instument_account_id_fkey'),
    sa.ForeignKeyConstraint(['currency_id'], ['currency_type.id'], name='instument_currency_id_fkey'),
    sa.ForeignKeyConstraint(['instument_type_id'], ['instument_type.id'], name='instument_instument_type_id_fkey'),
    sa.ForeignKeyConstraint(['operation_type_id'], ['operation_type.id'], name='instument_operation_type_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='instument_pkey')
    )
    op.drop_table('instrument')
    op.drop_table('instrument_type')
    # ### end Alembic commands ###
"""add table instument_type and foreign key instument_type for instruments

Revision ID: ba8c55fd5353
Revises: a1503105557b
Create Date: 2023-04-15 23:18:48.690418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba8c55fd5353'
down_revision = 'a1503105557b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('instument', sa.Column('instument_type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'instument', 'instument_type', ['instument_type_id'], ['id'])
    op.drop_column('instument', 'type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('instument', sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'instument', type_='foreignkey')
    op.drop_column('instument', 'instument_type_id')
    # ### end Alembic commands ###

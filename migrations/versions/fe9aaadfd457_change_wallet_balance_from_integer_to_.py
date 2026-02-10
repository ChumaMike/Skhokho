"""Change wallet_balance from integer to float

Revision ID: fe9aaadfd457
Revises: 7b902270fe0d
Create Date: 2026-02-10 19:29:40.509816

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fe9aaadfd457'
down_revision = '7b902270fe0d'
branch_labels = None
depends_on = None


def upgrade():
    # Create transaction table
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('related_user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['related_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Change wallet_balance from integer to float
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('wallet_balance',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)


def downgrade():
    # Drop transaction table
    op.drop_table('transaction')
    
    # Change wallet_balance back to integer
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('wallet_balance',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
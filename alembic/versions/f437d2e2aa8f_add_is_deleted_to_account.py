"""Add is_deleted to Account

Revision ID: f437d2e2aa8f
Revises: 27067910a228
Create Date: 2019-02-02 07:56:08.178036

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f437d2e2aa8f'
down_revision = '27067910a228'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'accounts',
        sa.Column(
            'initial_balance', sa.Float(), nullable=False, server_default="0"
        )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts', 'initial_balance')
    # ### end Alembic commands ###
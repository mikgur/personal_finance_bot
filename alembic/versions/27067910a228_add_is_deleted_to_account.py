"""add is_deleted to Account

Revision ID: 27067910a228
Revises: 88883c122634
Create Date: 2019-01-31 20:26:22.314565

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27067910a228'
down_revision = '88883c122634'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'accounts',
        sa.Column(
            'is_deleted', sa.Boolean(), nullable=False, server_default="false"
        )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts', 'is_deleted')
    # ### end Alembic commands ###

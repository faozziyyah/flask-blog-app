"""added post pic column

Revision ID: dac71a5b0f65
Revises: 0a5091a2488c
Create Date: 2022-09-14 11:27:26.179673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dac71a5b0f65'
down_revision = '0a5091a2488c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('post_pic', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'post_pic')
    # ### end Alembic commands ###

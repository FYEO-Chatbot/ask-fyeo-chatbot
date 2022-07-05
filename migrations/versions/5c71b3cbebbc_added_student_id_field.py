"""added student id field

Revision ID: 5c71b3cbebbc
Revises: 03b246095354
Create Date: 2022-07-05 03:20:08.901022

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c71b3cbebbc'
down_revision = '03b246095354'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conversation', sa.Column('student_id', sa.String(length=200), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('conversation', 'student_id')
    # ### end Alembic commands ###

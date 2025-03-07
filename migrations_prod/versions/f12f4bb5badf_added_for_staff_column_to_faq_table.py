"""added for_staff column to faq table

Revision ID: f12f4bb5badf
Revises: a9384ea5391d
Create Date: 2025-03-07 15:18:59.168168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f12f4bb5badf'
down_revision = 'a9384ea5391d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('faq', schema=None) as batch_op:
        batch_op.add_column(sa.Column('for_staff', sa.Boolean(), nullable=True))

    op.execute("UPDATE faq SET for_staff = FALSE WHERE for_staff IS NULL")
    
    # Alter column to NOT NULL and add unique constraint
    with op.batch_alter_table('faq', schema=None) as batch_op:
        batch_op.alter_column('for_staff', nullable=False)
        batch_op.drop_constraint('faq_tag_key', type_='unique')
        batch_op.create_unique_constraint('unique_faq_tag', ['tag', 'for_staff'])

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('faq', schema=None) as batch_op:
        batch_op.drop_constraint('unique_faq_tag', type_='unique')
        batch_op.create_unique_constraint('faq_tag_key', ['tag'])
        batch_op.drop_column('for_staff')

    # ### end Alembic commands ###

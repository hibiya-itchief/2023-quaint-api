"""group tag uniqueconstraint

Revision ID: a1cee85ccc50
Revises: 69b0d4a548fc
Create Date: 2022-09-03 14:38:27.172063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1cee85ccc50'
down_revision = '69b0d4a548fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_idx_groupid_tagid', 'grouptag', ['group_id', 'tag_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_idx_groupid_tagid', 'grouptag', type_='unique')
    # ### end Alembic commands ###
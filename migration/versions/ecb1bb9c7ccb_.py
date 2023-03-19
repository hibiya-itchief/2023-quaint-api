"""empty message

Revision ID: ecb1bb9c7ccb
Revises: 
Create Date: 2023-03-17 20:54:13.227150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecb1bb9c7ccb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('groupname', sa.VARCHAR(length=255), nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.Column('enable_vote', sa.Boolean(), nullable=True),
    sa.Column('twitter_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('instagram_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('stream_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('public_thumbnail_image_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('public_page_content_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('private_page_content_url', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_groups_groupname'), 'groups', ['groupname'], unique=False)
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=True)
    op.create_table('tags',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('tagname', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tagname')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=True)
    op.create_table('events',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('group_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('eventname', sa.VARCHAR(length=255), nullable=True),
    sa.Column('starts_at', sa.DateTime(), nullable=False),
    sa.Column('ends_at', sa.DateTime(), nullable=False),
    sa.Column('sell_starts', sa.DateTime(), nullable=False),
    sa.Column('sell_ends', sa.DateTime(), nullable=False),
    sa.Column('lottery', sa.Boolean(), nullable=True),
    sa.Column('target', sa.VARCHAR(length=255), nullable=False),
    sa.Column('ticket_stock', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=True)
    op.create_table('groupowners',
    sa.Column('group_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'user_id')
    )
    op.create_table('grouptag',
    sa.Column('group_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('tag_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'tag_id'),
    sa.UniqueConstraint('group_id', 'tag_id', name='unique_idx_groupid_tagid')
    )
    op.create_table('votes',
    sa.Column('group_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('tickets',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('group_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column('event_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column('owner_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column('person', sa.Integer(), nullable=True),
    sa.Column('is_family_ticket', sa.Boolean(), nullable=True),
    sa.Column('is_used', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tickets_id'), table_name='tickets')
    op.drop_table('tickets')
    op.drop_table('votes')
    op.drop_table('grouptag')
    op.drop_table('groupowners')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_groups_id'), table_name='groups')
    op.drop_index(op.f('ix_groups_groupname'), table_name='groups')
    op.drop_table('groups')
    # ### end Alembic commands ###
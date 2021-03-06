"""empty message

Revision ID: 1485bc687ec4
Revises: 16e4683a7e16
Create Date: 2021-10-23 14:03:58.635741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1485bc687ec4'
down_revision = '16e4683a7e16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Venue_shows')
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    op.create_table('Venue_shows',
    sa.Column('venu_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['show_id'], ['Show.id'], name='Venue_shows_show_id_fkey'),
    sa.ForeignKeyConstraint(['venu_id'], ['Venue.id'], name='Venue_shows_venu_id_fkey'),
    sa.PrimaryKeyConstraint('venu_id', 'show_id', name='Venue_shows_pkey')
    )
    # ### end Alembic commands ###

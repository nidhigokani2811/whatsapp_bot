"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-06-26 23:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create restaurants table
    op.create_table(
        'restaurants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restaurants_id'), 'restaurants', ['id'], unique=False)

    # 2. Create whatsapp_accounts table
    op.create_table(
        'whatsapp_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('phone_number_id', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=False),
        sa.Column('waba_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_accounts_id'), 'whatsapp_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_whatsapp_accounts_phone_number_id'), 'whatsapp_accounts', ['phone_number_id'], unique=True)

    # 3. Create whatsapp_webhook_events table
    op.create_table(
        'whatsapp_webhook_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=True),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_webhook_events_id'), 'whatsapp_webhook_events', ['id'], unique=False)

    # 4. Create whatsapp_contacts table
    op.create_table(
        'whatsapp_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('whatsapp_number', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_contacts_id'), 'whatsapp_contacts', ['id'], unique=False)
    op.create_index(op.f('ix_whatsapp_contacts_whatsapp_number'), 'whatsapp_contacts', ['whatsapp_number'], unique=False)

    # 5. Create whatsapp_messages table
    op.create_table(
        'whatsapp_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('whatsapp_message_id', sa.String(length=255), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=20), nullable=False),
        sa.Column('text_message', sa.Text(), nullable=True),
        sa.Column('media_id', sa.String(length=255), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['whatsapp_contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_messages_id'), 'whatsapp_messages', ['id'], unique=False)
    op.create_index(op.f('ix_whatsapp_messages_whatsapp_message_id'), 'whatsapp_messages', ['whatsapp_message_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_whatsapp_messages_whatsapp_message_id'), table_name='whatsapp_messages')
    op.drop_index(op.f('ix_whatsapp_messages_id'), table_name='whatsapp_messages')
    op.drop_table('whatsapp_messages')
    
    op.drop_index(op.f('ix_whatsapp_contacts_whatsapp_number'), table_name='whatsapp_contacts')
    op.drop_index(op.f('ix_whatsapp_contacts_id'), table_name='whatsapp_contacts')
    op.drop_table('whatsapp_contacts')

    op.drop_index(op.f('ix_whatsapp_webhook_events_id'), table_name='whatsapp_webhook_events')
    op.drop_table('whatsapp_webhook_events')

    op.drop_index(op.f('ix_whatsapp_accounts_phone_number_id'), table_name='whatsapp_accounts')
    op.drop_index(op.f('ix_whatsapp_accounts_id'), table_name='whatsapp_accounts')
    op.drop_table('whatsapp_accounts')

    op.drop_index(op.f('ix_restaurants_id'), table_name='restaurants')
    op.drop_table('restaurants')

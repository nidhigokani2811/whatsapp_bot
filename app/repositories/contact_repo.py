from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from app.models.models import WhatsAppContact

class ContactRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, contact_id: int) -> Optional[WhatsAppContact]:
        result = await self.db.execute(select(WhatsAppContact).filter(WhatsAppContact.id == contact_id))
        return result.scalar_one_or_none()

    async def get_by_number(self, restaurant_id: int, whatsapp_number: str) -> Optional[WhatsAppContact]:
        result = await self.db.execute(
            select(WhatsAppContact).filter(
                WhatsAppContact.restaurant_id == restaurant_id,
                WhatsAppContact.whatsapp_number == whatsapp_number
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[WhatsAppContact]:
        result = await self.db.execute(select(WhatsAppContact).order_by(WhatsAppContact.id).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_or_update(self, restaurant_id: int, whatsapp_number: str, display_name: Optional[str] = None) -> WhatsAppContact:
        contact = await self.get_by_number(restaurant_id, whatsapp_number)
        if contact:
            if display_name and contact.display_name != display_name:
                contact.display_name = display_name
                await self.db.flush()
        else:
            contact = WhatsAppContact(
                restaurant_id=restaurant_id,
                whatsapp_number=whatsapp_number,
                display_name=display_name
            )
            self.db.add(contact)
            await self.db.flush()
        return contact

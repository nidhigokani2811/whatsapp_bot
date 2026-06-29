from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from datetime import datetime
from app.models.models import WhatsAppMessage

class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, message_id: int) -> Optional[WhatsAppMessage]:
        result = await self.db.execute(select(WhatsAppMessage).filter(WhatsAppMessage.id == message_id))
        return result.scalar_one_or_none()

    async def get_by_whatsapp_id(self, whatsapp_message_id: str) -> Optional[WhatsAppMessage]:
        result = await self.db.execute(
            select(WhatsAppMessage).filter(WhatsAppMessage.whatsapp_message_id == whatsapp_message_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100, restaurant_id: Optional[int] = None, contact_id: Optional[int] = None
    ) -> Sequence[WhatsAppMessage]:
        query = select(WhatsAppMessage)
        if restaurant_id is not None:
            query = query.filter(WhatsAppMessage.restaurant_id == restaurant_id)
        if contact_id is not None:
            query = query.filter(WhatsAppMessage.contact_id == contact_id)
        query = query.order_by(WhatsAppMessage.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(
        self,
        restaurant_id: int,
        contact_id: int,
        whatsapp_message_id: str,
        message_type: str,
        direction: str = "incoming",
        text_message: Optional[str] = None,
        media_id: Optional[str] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> WhatsAppMessage:
        message = WhatsAppMessage(
            restaurant_id=restaurant_id,
            contact_id=contact_id,
            whatsapp_message_id=whatsapp_message_id,
            message_type=message_type,
            direction=direction,
            text_message=text_message,
            media_id=media_id,
            filename=filename,
            mime_type=mime_type,
            created_at=created_at or datetime.utcnow()
        )
        self.db.add(message)
        await self.db.flush()
        return message

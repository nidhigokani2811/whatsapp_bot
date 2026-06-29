from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence
from datetime import datetime
from app.models.models import WhatsAppWebhookEvent

class WebhookEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, event_id: int) -> Optional[WhatsAppWebhookEvent]:
        result = await self.db.execute(select(WhatsAppWebhookEvent).filter(WhatsAppWebhookEvent.id == event_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[WhatsAppWebhookEvent]:
        result = await self.db.execute(
            select(WhatsAppWebhookEvent)
            .order_by(WhatsAppWebhookEvent.received_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        raw_payload: dict,
        restaurant_id: Optional[int] = None
    ) -> WhatsAppWebhookEvent:
        event = WhatsAppWebhookEvent(
            restaurant_id=restaurant_id,
            raw_payload=raw_payload,
            received_at=datetime.utcnow()
        )
        self.db.add(event)
        await self.db.flush()
        return event

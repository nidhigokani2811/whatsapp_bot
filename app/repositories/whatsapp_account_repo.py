from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from app.models.models import WhatsAppAccount

class WhatsAppAccountRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, account_id: int) -> Optional[WhatsAppAccount]:
        result = await self.db.execute(select(WhatsAppAccount).filter(WhatsAppAccount.id == account_id))
        return result.scalar_one_or_none()

    async def get_by_phone_number_id(self, phone_number_id: str) -> Optional[WhatsAppAccount]:
        result = await self.db.execute(
            select(WhatsAppAccount).filter(WhatsAppAccount.phone_number_id == phone_number_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[WhatsAppAccount]:
        result = await self.db.execute(select(WhatsAppAccount).order_by(WhatsAppAccount.id).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(
        self,
        restaurant_id: int,
        waba_id: str,
        phone_number_id: str,
        phone_number: str,
        access_token: str,
        status: str = "connected"
    ) -> WhatsAppAccount:
        account = WhatsAppAccount(
            restaurant_id=restaurant_id,
            waba_id=waba_id,
            phone_number_id=phone_number_id,
            phone_number=phone_number,
            access_token=access_token,
            status=status
        )
        self.db.add(account)
        await self.db.flush()
        return account

    async def delete(self, account_id: int) -> bool:
        account = await self.get_by_id(account_id)
        if account:
            await self.db.delete(account)
            await self.db.flush()
            return True
        return False

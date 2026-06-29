from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from app.models.models import Restaurant

class RestaurantRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        result = await self.db.execute(select(Restaurant).filter(Restaurant.id == restaurant_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Restaurant]:
        result = await self.db.execute(select(Restaurant).order_by(Restaurant.id).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, name: str, email: Optional[str] = None) -> Restaurant:
        restaurant = Restaurant(name=name, email=email)
        self.db.add(restaurant)
        await self.db.flush()
        return restaurant

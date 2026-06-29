import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.session import get_db
from app.schemas.schemas import (
    RestaurantOut, RestaurantCreate,
    WhatsAppAccountOut, WhatsAppAccountConnect,
    ContactOut, MessageOut, WebhookEventOut
)
from app.repositories.restaurant_repo import RestaurantRepository
from app.repositories.whatsapp_account_repo import WhatsAppAccountRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.webhook_event_repo import WebhookEventRepository

logger = logging.getLogger("api_router")
router = APIRouter(tags=["POC API Endpoints"])

# --- Restaurant Endpoints ---

@router.post("/restaurants", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    payload: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
) -> RestaurantOut:
    """Create a new Restaurant context (for manual configuration)."""
    repo = RestaurantRepository(db)
    return await repo.create(name=payload.name, email=payload.email)


@router.get("/restaurants", response_model=List[RestaurantOut])
async def list_restaurants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantOut]:
    """Retrieve all restaurants."""
    repo = RestaurantRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/restaurants/{id}", response_model=RestaurantOut)
async def get_restaurant(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> RestaurantOut:
    """Retrieve details of a single restaurant."""
    repo = RestaurantRepository(db)
    restaurant = await repo.get_by_id(id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found."
        )
    return restaurant


# --- WhatsApp Account Endpoints ---

@router.post("/restaurants/{restaurant_id}/whatsapp-accounts", response_model=WhatsAppAccountOut, status_code=status.HTTP_201_CREATED)
async def connect_whatsapp_account(
    restaurant_id: int,
    payload: WhatsAppAccountConnect,
    db: AsyncSession = Depends(get_db)
) -> WhatsAppAccountOut:
    """Manually map a WhatsApp Business Account (WABA) credentials to a restaurant."""
    rest_repo = RestaurantRepository(db)
    restaurant = await rest_repo.get_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found."
        )

    repo = WhatsAppAccountRepository(db)
    existing = await repo.get_by_phone_number_id(payload.phone_number_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A WhatsApp account with this phone number ID is already registered."
        )

    account = await repo.create(
        restaurant_id=restaurant_id,
        waba_id=payload.waba_id,
        phone_number_id=payload.phone_number_id,
        phone_number=payload.phone_number,
        access_token=payload.access_token,
        status=payload.status or "connected"
    )
    return account


# --- Contact Endpoints ---

@router.get("/contacts", response_model=List[ContactOut])
async def list_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[ContactOut]:
    """List contacts belonging to all WABA accounts."""
    repo = ContactRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


# --- Message Endpoints ---

@router.get("/messages", response_model=List[MessageOut])
async def list_messages(
    restaurant_id: Optional[int] = None,
    contact_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[MessageOut]:
    """Retrieve all logged messages with optional filters."""
    repo = MessageRepository(db)
    return await repo.get_all(skip=skip, limit=limit, restaurant_id=restaurant_id, contact_id=contact_id)


@router.get("/messages/{id}", response_model=MessageOut)
async def get_message(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> MessageOut:
    """Retrieve a single message log."""
    repo = MessageRepository(db)
    message = await repo.get_by_id(id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found."
        )
    return message


# --- Webhook Event Endpoints ---

@router.get("/webhook-events", response_model=List[WebhookEventOut])
async def list_webhook_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[WebhookEventOut]:
    """Retrieve raw webhook logs."""
    repo = WebhookEventRepository(db)
    return await repo.get_all(skip=skip, limit=limit)

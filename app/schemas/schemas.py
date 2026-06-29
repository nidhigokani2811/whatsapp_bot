from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from typing import List, Optional

# --- REST API Schemas ---

class RestaurantCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None

class RestaurantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: Optional[str] = None
    created_at: datetime


class WhatsAppAccountConnect(BaseModel):
    waba_id: str
    phone_number_id: str
    phone_number: str
    access_token: str
    status: Optional[str] = "connected"

class WhatsAppAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    restaurant_id: int
    phone_number_id: str
    phone_number: str
    waba_id: str
    status: str
    created_at: datetime


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    restaurant_id: int
    whatsapp_number: str
    display_name: Optional[str] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    restaurant_id: int
    contact_id: int
    whatsapp_message_id: str
    message_type: str
    direction: str
    text_message: Optional[str] = None
    media_id: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: datetime


class WebhookEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    restaurant_id: Optional[int] = None
    raw_payload: dict
    received_at: datetime


# --- Meta WhatsApp Webhook Ingestion Schemas ---

class ProfileSchema(BaseModel):
    name: Optional[str] = None

class ContactWebhook(BaseModel):
    profile: Optional[ProfileSchema] = None
    wa_id: str

class MetadataWebhook(BaseModel):
    display_phone_number: str
    phone_number_id: str

class TextWebhook(BaseModel):
    body: str

class MediaWebhook(BaseModel):
    id: str
    mime_type: Optional[str] = None
    sha256: Optional[str] = None
    filename: Optional[str] = None
    caption: Optional[str] = None

class MessageWebhook(BaseModel):
    id: str
    from_: str = Field(alias="from")
    timestamp: str
    type: str
    text: Optional[TextWebhook] = None
    image: Optional[MediaWebhook] = None
    document: Optional[MediaWebhook] = None
    audio: Optional[MediaWebhook] = None
    video: Optional[MediaWebhook] = None
    
    model_config = ConfigDict(populate_by_name=True)

class StatusWebhook(BaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str

class ValueWebhook(BaseModel):
    messaging_product: str
    metadata: Optional[MetadataWebhook] = None
    contacts: Optional[List[ContactWebhook]] = None
    messages: Optional[List[MessageWebhook]] = None
    statuses: Optional[List[StatusWebhook]] = None

class ChangeWebhook(BaseModel):
    value: ValueWebhook
    field: str

class EntryWebhook(BaseModel):
    id: str
    changes: List[ChangeWebhook]

class WebhookPayload(BaseModel):
    object: str
    entry: List[EntryWebhook]

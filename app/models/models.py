from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from app.database.base import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    whatsapp_accounts: Mapped[List["WhatsAppAccount"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")
    contacts: Mapped[List["WhatsAppContact"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")
    messages: Mapped[List["WhatsAppMessage"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")
    webhook_events: Mapped[List["WhatsAppWebhookEvent"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Restaurant(id={self.id}, name={self.name})>"


class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    phone_number_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    waba_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="connected", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(back_populates="whatsapp_accounts")

    def __repr__(self) -> str:
        return f"<WhatsAppAccount(id={self.id}, restaurant_id={self.restaurant_id}, phone_number_id={self.phone_number_id})>"


class WhatsAppWebhookEvent(Base):
    __tablename__ = "whatsapp_webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    restaurant: Mapped[Optional["Restaurant"]] = relationship(back_populates="webhook_events")

    def __repr__(self) -> str:
        return f"<WhatsAppWebhookEvent(id={self.id}, restaurant_id={self.restaurant_id})>"


class WhatsAppContact(Base):
    __tablename__ = "whatsapp_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    whatsapp_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(back_populates="contacts")
    messages: Mapped[List["WhatsAppMessage"]] = relationship(back_populates="contact", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<WhatsAppContact(id={self.id}, number={self.whatsapp_number}, name={self.display_name})>"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("whatsapp_contacts.id", ondelete="CASCADE"), nullable=False)
    whatsapp_message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="incoming", nullable=False)
    text_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(back_populates="messages")
    contact: Mapped["WhatsAppContact"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<WhatsAppMessage(id={self.id}, type={self.message_type}, direction={self.direction})>"

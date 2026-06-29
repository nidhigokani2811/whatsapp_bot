import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.whatsapp_account_repo import WhatsAppAccountRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.webhook_event_repo import WebhookEventRepository
from app.schemas.schemas import WebhookPayload

logger = logging.getLogger("whatsapp_service")

class WhatsAppService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def process_webhook_payload(self, payload: WebhookPayload, raw_body: dict) -> None:
        """Processes incoming webhook updates from WhatsApp, resolves the restaurant tenant,
        logs the raw event, creates/updates contacts, and parses and stores messages.
        """
        logger.info("Incoming webhook received")

        account_repo = WhatsAppAccountRepository(self.db)
        event_repo = WebhookEventRepository(self.db)

        for entry in payload.entry:
            for change in entry.changes:
                value = change.value
                
                # 1. Extract phone_number_id
                phone_number_id = ""
                if value.metadata:
                    phone_number_id = value.metadata.phone_number_id

                if not phone_number_id:
                    logger.warning("Incoming webhook payload missing WABA phone_number_id. Skipping.")
                    continue

                # 2. Find the corresponding restaurant/account
                account = await account_repo.get_by_phone_number_id(phone_number_id)
                if not account:
                    logger.error(f"Unknown phone_number_id: {phone_number_id}")
                    # Log the raw event even if the restaurant is unknown (but with restaurant_id=None)
                    await event_repo.create(raw_payload=raw_body, restaurant_id=None)
                    await self.db.commit()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"WhatsApp account not found for phone_number_id: {phone_number_id}"
                    )

                restaurant_id = account.restaurant_id
                logger.info(f"Restaurant identified: id={restaurant_id} for WABA phone ID={phone_number_id}")

                # 3. Store raw webhook JSON payload in database
                await event_repo.create(raw_payload=raw_body, restaurant_id=restaurant_id)

                if not value.messages:
                    logger.debug("No messages in webhook value update. Skipping thread processing.")
                    continue

                contact_repo = ContactRepository(self.db)
                message_repo = MessageRepository(self.db)

                # Resolve profile display names by whatsapp ID
                profile_names = {}
                if value.contacts:
                    for c in value.contacts:
                        display_name = c.profile.name if c.profile else None
                        profile_names[c.wa_id] = display_name

                for message in value.messages:
                    wa_number = message.from_
                    display_name = profile_names.get(wa_number)

                    # 4. Extract contact and create/update
                    contact = await contact_repo.create_or_update(
                        restaurant_id=restaurant_id,
                        whatsapp_number=wa_number,
                        display_name=display_name
                    )

                    # 5. Check message idempotency
                    existing = await message_repo.get_by_whatsapp_id(message.id)
                    if existing:
                        logger.info(f"WhatsApp Message ID {message.id} has already been stored. Skipping.")
                        continue

                    # 6. Extract message content and media metadata
                    message_type = message.type
                    text_message = None
                    media_id = None
                    filename = None
                    mime_type = None

                    # Check if message type is supported
                    supported_types = ["text", "image", "document", "audio", "video"]
                    if message_type not in supported_types:
                        logger.warning(f"Unsupported message type: {message_type}")
                        # We still log the message as unsupported but with raw type
                        text_message = f"[Unsupported message type: {message_type}]"
                    else:
                        if message_type == "text" and message.text:
                            text_message = message.text.body
                        else:
                            # It's a media message
                            media_payload = None
                            if message_type == "image":
                                media_payload = message.image
                            elif message_type == "document":
                                media_payload = message.document
                            elif message_type == "audio":
                                media_payload = message.audio
                            elif message_type == "video":
                                media_payload = message.video

                            if media_payload:
                                media_id = media_payload.id
                                mime_type = media_payload.mime_type
                                filename = getattr(media_payload, "filename", None)
                                text_message = getattr(media_payload, "caption", None) or f"Sent {message_type}"

                    try:
                        timestamp = datetime.utcfromtimestamp(int(message.timestamp))
                    except (ValueError, TypeError):
                        timestamp = datetime.utcnow()

                    # 7. Store message information
                    await message_repo.create(
                        restaurant_id=restaurant_id,
                        contact_id=contact.id,
                        whatsapp_message_id=message.id,
                        message_type=message_type,
                        direction="incoming",
                        text_message=text_message,
                        media_id=media_id,
                        filename=filename,
                        mime_type=mime_type,
                        created_at=timestamp
                    )
                    logger.info(f"Message stored successfully: message_id={message.id}")

        await self.db.commit()

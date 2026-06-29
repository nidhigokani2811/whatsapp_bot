import logging
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.schemas import WebhookPayload
from app.services.whatsapp_service import WhatsAppService
from app.config.settings import settings

logger = logging.getLogger("webhook_router")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify_whatsapp_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
) -> str:
    """Handles GET challenge verification requests sent by Meta."""
    logger.info(f"Received webhook verification request. token={hub_verify_token}")
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verification succeeded.")
        return hub_challenge
    
    logger.warning("Webhook verification failed: token mismatch or incorrect mode.")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch or mode not supported."
    )


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def receive_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Receives incoming events from Meta WhatsApp Business Cloud API."""
    try:
        body_dict = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse request body as JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

    try:
        payload = WebhookPayload(**body_dict)
    except Exception as e:
        logger.error(f"Invalid webhook payload structure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload structure"
        )

    service = WhatsAppService(db)
    try:
        await service.process_webhook_payload(payload, body_dict)
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions (e.g. unknown phone_number_id)
        raise http_exc
    except Exception as e:
        logger.error(f"Database or system error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database errors"
        )

    return {"status": "success"}

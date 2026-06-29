import logging
from typing import Dict, List, Callable, Any, Awaitable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_dispatcher")

# Async event handler type signature
EventHandler = Callable[[str, Any], Awaitable[None]]

class EventDispatcher:
    """A lightweight, in-memory pub-sub dispatcher for system events.
    
    This is designed to decouple core WhatsApp ingestion from downstream actions,
    such as triggering OCR, AI invoice data extraction, or sending email notifications.
    """
    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}

    def register(self, event_name: str, handler: EventHandler) -> None:
        """Registers a callback function to run when a specific event occurs."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        handler_name = getattr(handler, "__name__", str(handler))
        logger.info(f"Registered event handler '{handler_name}' for event '{event_name}'")

    async def publish(self, event_name: str, data: Any) -> None:
        """Publishes an event, executing all registered callback handlers concurrently or sequentially."""
        logger.info(f"Publishing event '{event_name}' with payload: {data}")
        handlers = self._handlers.get(event_name, [])
        if not handlers:
            logger.debug(f"No handlers registered for event '{event_name}'")
            return

        for handler in handlers:
            try:
                await handler(event_name, data)
            except Exception as e:
                handler_name = getattr(handler, "__name__", str(handler))
                logger.error(
                    f"Error in event handler '{handler_name}' for event '{event_name}': {str(e)}", 
                    exc_info=True
                )

# Global dispatcher instance
event_dispatcher = EventDispatcher()


# --- Default Event Subscribers / Mocks ---

async def handle_invoice_received(event_name: str, data: Any) -> None:
    """Mock handler simulating a future invoice processing microservice or worker."""
    logger.info("=" * 60)
    logger.info(f"[EVENT RECEIVED] Event: {event_name}")
    logger.info(f" - Media ID: {data.get('media_id')}")
    logger.info(f" - Local File Path: {data.get('local_path')}")
    logger.info(f" - Mime Type: {data.get('mime_type')}")
    logger.info(f" - Filename: {data.get('original_filename')}")
    logger.info(" -> Action: Queuing file for OCR scanning and LLM extraction...")
    logger.info("=" * 60)

# Register the default handler so that we see the flow work end-to-end
event_dispatcher.register("invoice_received", handle_invoice_received)

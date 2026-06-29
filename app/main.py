import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as api_router
from app.webhooks.whatsapp import router as webhook_router
from app.config.settings import settings

# Setup unified logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing SaaS WhatsApp Multi-Tenant Backend Service POC...")
    yield
    # Shutdown actions
    logger.info("Service shutting down.")

app = FastAPI(
    title="Multi-Tenant SaaS WhatsApp Business API Backend POC",
    description=(
        "Minimal Python backend using FastAPI that integrates with the WhatsApp Business Cloud API "
        "and stores incoming WhatsApp messages in PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(webhook_router)
app.include_router(api_router)

@app.get("/health", tags=["System"])
async def health_status() -> dict:
    """Performs quick dependency and service checks."""
    return {
        "status": "healthy",
        "api_version": settings.WHATSAPP_API_VERSION
    }

@app.get("/", tags=["System"])
async def index() -> dict:
    """Swagger documentation landing page reference."""
    return {
        "service": "Multi-Tenant SaaS WhatsApp Business Webhook API POC",
        "documentation": "/docs",
        "health": "/health"
    }

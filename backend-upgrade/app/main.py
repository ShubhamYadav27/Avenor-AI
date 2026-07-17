"""
Avenor — Predictive Revenue Intelligence
FastAPI application entry point.
"""
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
 
from app.core.config import settings
from app.core.exceptions import AvenorError, NotFoundError, AuthenticationError, AuthorizationError
from app.core.logging import configure_logging, get_logger
from app.db.session import init_db
 
configure_logging()
logger = get_logger(__name__)
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("avenor_starting", env=settings.APP_ENV)
    try:
        init_db()
        logger.info("database_ready")
    except Exception as e:
        logger.warning("database_unavailable", error=str(e))
        if settings.is_production:
            raise  # hard fail in production
        # In development, allow startup without DB (useful for testing OpenAPI)
    yield
    logger.info("avenor_shutting_down")
 
 
# ── Sentry ────────────────────────────────────────────────────
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=0.1,
    )
 
# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Avenor — Predictive Revenue Intelligence",
    description=(
        "Know who is about to buy, why, and what to say — "
        "before any competitor does."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
 
# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# ── Exception handlers ────────────────────────────────────────
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": exc.message, "code": exc.code})
 
 
@app.exception_handler(AuthenticationError)
async def auth_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"error": exc.message, "code": exc.code})
 
 
@app.exception_handler(AuthorizationError)
async def authz_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(status_code=403, content={"error": exc.message, "code": exc.code})
 
 
@app.exception_handler(AvenorError)
async def avenor_error_handler(request: Request, exc: AvenorError):
    return JSONResponse(status_code=500, content={"error": exc.message, "code": exc.code})
 
 
# ── Root ──────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "Avenor Predictive Revenue Intelligence",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
 
 
# ── Routers ───────────────────────────────────────────────────
from app.api.routes.auth import router as auth_router
from app.api.routes.icp import router as icp_router
from app.api.routes.feed import router as feed_router
from app.api.routes.signals import router as signals_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.companies import router as companies_router
from app.api.routes.outcomes import router as outcomes_router
from app.api.routes.health import router as health_router
from app.integrations.hubspot.routes import router as hubspot_router
from app.api.routes.intelligence import router as intelligence_router
 
API_PREFIX = "/api/v1"

app.include_router(health_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(icp_router, prefix=API_PREFIX)
app.include_router(feed_router, prefix=API_PREFIX)
app.include_router(signals_router, prefix=API_PREFIX)
app.include_router(contacts_router, prefix=API_PREFIX)
app.include_router(companies_router, prefix=API_PREFIX)
app.include_router(outcomes_router, prefix=API_PREFIX)
app.include_router(hubspot_router, prefix=API_PREFIX)
app.include_router(intelligence_router, prefix=API_PREFIX)
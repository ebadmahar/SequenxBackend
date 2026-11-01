from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.file_service import BLOG_IMAGES_DIR, ensure_upload_dirs
from app.utils.rate_limit import limiter

try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    has_slowapi = True
except ImportError:
    has_slowapi = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle application startup and shutdown events."""
    # 1. Ensure private and public upload directories exist
    ensure_upload_dirs()

    # 2. Seed database schema and initial administrator
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Attach rate limiter to FastAPI state & exception handlers if slowapi is present
app.state.limiter = limiter
if has_slowapi:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.ebadmahar\.site|https://.*\.netlify\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount public blog images and site assets directories as static assets (CVs directory is strictly private)
ensure_upload_dirs()
app.mount(
    "/static/blog_images",
    StaticFiles(directory=str(BLOG_IMAGES_DIR)),
    name="blog_images",
)
# app.mount(
#     "/static/site_assets",
#     StaticFiles(directory=str(SITE_ASSETS_DIR)),
#     name="site_assets",
# )

# Register consolidated API routers
app.include_router(api_router)

@app.get(
    "/health",
    tags=["Health"],
    summary="API Health Status",
    description="Check the current health and status of the service.",
)
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_VERSION,
    }

@app.get(
    "/",
    tags=["Root"],
    include_in_schema=False,
)
def root():
    return {
        "title": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc",
    }

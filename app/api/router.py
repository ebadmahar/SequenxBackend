from fastapi import APIRouter

from app.api.admin.applications import router as admin_applications_router
from app.api.admin.auth import router as auth_router
from app.api.admin.blog import router as admin_blog_router
from app.api.admin.jobs import router as admin_jobs_router
from app.api.admin.messages import router as admin_messages_router
from app.api.admin.newsletter import router as admin_newsletter_router
from app.api.admin.settings import router as admin_settings_router
from app.api.admin.site_assets import router as admin_site_assets_router
from app.api.admin.stats import router as admin_stats_router
from app.api.admin.users import router as admin_users_router
from app.api.public.analytics import router as public_analytics_router
from app.api.public.blog import router as public_blog_router
from app.api.public.contact import router as public_contact_router
from app.api.public.jobs import router as public_jobs_router
from app.api.public.newsletter import router as public_newsletter_router
from app.api.public.site_assets import router as public_site_assets_router

api_router = APIRouter()

# Public Routes
api_router.include_router(public_blog_router)
api_router.include_router(public_jobs_router)
api_router.include_router(public_contact_router)
api_router.include_router(public_analytics_router)
api_router.include_router(public_newsletter_router)
api_router.include_router(public_site_assets_router)

# Authentication Routes
api_router.include_router(auth_router)

# Admin & Staff Protected Routes
api_router.include_router(admin_stats_router)
api_router.include_router(admin_blog_router)
api_router.include_router(admin_jobs_router)
api_router.include_router(admin_applications_router)
api_router.include_router(admin_messages_router)
api_router.include_router(admin_newsletter_router)
api_router.include_router(admin_users_router)
api_router.include_router(admin_settings_router)
api_router.include_router(admin_site_assets_router)

from fastapi import APIRouter

from app.api.routes import (
    auth,
    briefings,
    companies,
    contacts,
    emails,
    feed,
    health,
    icp,
    intelligence,
    outcomes,
    research,
    sales_coaching,
    signals,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(briefings.router)
api_router.include_router(companies.router)
api_router.include_router(contacts.router)
api_router.include_router(emails.router)
api_router.include_router(feed.router)
api_router.include_router(health.router)
api_router.include_router(icp.router)
api_router.include_router(intelligence.router)
api_router.include_router(outcomes.router)
api_router.include_router(research.router)
api_router.include_router(sales_coaching.router)
api_router.include_router(signals.router)

from app.crm import routes as crm_routes
api_router.include_router(crm_routes.router)
api_router.include_router(crm_routes.integrations_crm_router)

from app.integrations.hubspot import routes as hubspot_routes
api_router.include_router(hubspot_routes.router)

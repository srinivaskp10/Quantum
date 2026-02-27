from fastapi import APIRouter
from app.api import auth, users, leads, customers, campaigns, sales_records, ai, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(sales_records.router, prefix="/sales", tags=["Sales Records"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Features"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

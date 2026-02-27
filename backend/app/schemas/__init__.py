from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadBulkUpload
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.schemas.sales_record import SalesRecordCreate, SalesRecordUpdate, SalesRecordResponse
from app.schemas.ai import (
    LeadScoreRequest, LeadScoreResponse,
    ChatRequest, ChatResponse,
    ContentGenerateRequest, ContentGenerateResponse,
    InsightRequest, InsightResponse
)

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token",
    "LeadCreate", "LeadUpdate", "LeadResponse", "LeadBulkUpload",
    "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    "CampaignCreate", "CampaignUpdate", "CampaignResponse",
    "SalesRecordCreate", "SalesRecordUpdate", "SalesRecordResponse",
    "LeadScoreRequest", "LeadScoreResponse",
    "ChatRequest", "ChatResponse",
    "ContentGenerateRequest", "ContentGenerateResponse",
    "InsightRequest", "InsightResponse"
]

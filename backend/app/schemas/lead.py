from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.lead import LeadStatus, LeadSource


class LeadBase(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[float] = None
    location: Optional[str] = None
    source: LeadSource = LeadSource.OTHER
    estimated_value: Optional[float] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    assigned_to: Optional[int] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[float] = None
    location: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None


class LeadResponse(LeadBase):
    id: int
    status: LeadStatus
    ai_score: Optional[float] = None
    ai_score_reasoning: Optional[str] = None
    ai_score_updated_at: Optional[datetime] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_contact_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadBulkUpload(BaseModel):
    leads: List[LeadCreate]


class LeadWithScore(LeadResponse):
    ai_score: Optional[float] = None
    ai_score_reasoning: Optional[str] = None

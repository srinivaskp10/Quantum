from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.campaign import CampaignStatus, CampaignType


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType = CampaignType.EMAIL
    target_audience: Optional[str] = None
    target_industry: Optional[str] = None
    budget: float = 0
    content: Optional[str] = None


class CampaignCreate(CampaignBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    target_audience: Optional[str] = None
    target_industry: Optional[str] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    leads_generated: Optional[int] = None
    revenue_attributed: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    content: Optional[str] = None


class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatus
    spent: float
    impressions: int
    clicks: int
    conversions: int
    leads_generated: int
    revenue_attributed: float
    click_through_rate: float
    conversion_rate: float
    cost_per_lead: float
    roi: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

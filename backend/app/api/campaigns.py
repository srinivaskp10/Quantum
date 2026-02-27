from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter()


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CampaignStatus] = None,
    campaign_type: Optional[CampaignType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List campaigns with optional filters."""
    query = db.query(Campaign)
    
    if status:
        query = query.filter(Campaign.status == status)
    if campaign_type:
        query = query.filter(Campaign.campaign_type == campaign_type)
    
    campaigns = query.offset(skip).limit(limit).all()
    return campaigns


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MARKETING]))
):
    """Create a new campaign (Admin/Marketing only)."""
    campaign = Campaign(**campaign_data.model_dump())
    campaign.created_by = current_user.id
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MARKETING]))
):
    """Update a campaign (Admin/Marketing only)."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    # Recalculate derived metrics
    campaign.update_metrics()
    
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/update-metrics", response_model=CampaignResponse)
def update_campaign_metrics(
    campaign_id: int,
    impressions: Optional[int] = None,
    clicks: Optional[int] = None,
    conversions: Optional[int] = None,
    leads_generated: Optional[int] = None,
    revenue_attributed: Optional[float] = None,
    spent: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MARKETING]))
):
    """Update campaign performance metrics."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if impressions is not None:
        campaign.impressions = impressions
    if clicks is not None:
        campaign.clicks = clicks
    if conversions is not None:
        campaign.conversions = conversions
    if leads_generated is not None:
        campaign.leads_generated = leads_generated
    if revenue_attributed is not None:
        campaign.revenue_attributed = revenue_attributed
    if spent is not None:
        campaign.spent = spent
    
    campaign.update_metrics()
    
    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a campaign (Admin only)."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()
    return None

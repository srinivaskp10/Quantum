from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lead import Lead, LeadStatus
from app.models.customer import Customer
from app.models.campaign import Campaign, CampaignStatus
from app.models.sales_record import SalesRecord, DealStage

router = APIRouter()


@router.get("/kpis")
def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get key performance indicators."""
    # Total revenue (closed won deals)
    total_revenue = db.query(func.sum(SalesRecord.amount)).filter(
        SalesRecord.stage == DealStage.CLOSED_WON
    ).scalar() or 0
    
    # Total leads
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    
    # Converted leads
    converted_leads = db.query(func.count(Lead.id)).filter(
        Lead.status == LeadStatus.CLOSED_WON
    ).scalar() or 0
    
    # Conversion rate
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Active campaigns
    active_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.status == CampaignStatus.ACTIVE
    ).scalar() or 0
    
    # Total customers
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    
    # Pipeline value (open deals)
    pipeline_value = db.query(func.sum(SalesRecord.amount)).filter(
        SalesRecord.stage.not_in([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
    ).scalar() or 0
    
    # Average deal size
    avg_deal_size = db.query(func.avg(SalesRecord.amount)).filter(
        SalesRecord.stage == DealStage.CLOSED_WON
    ).scalar() or 0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_leads": total_leads,
        "converted_leads": converted_leads,
        "conversion_rate": round(conversion_rate, 2),
        "active_campaigns": active_campaigns,
        "total_customers": total_customers,
        "pipeline_value": round(pipeline_value, 2),
        "average_deal_size": round(avg_deal_size, 2)
    }


@router.get("/revenue-over-time")
def get_revenue_over_time(
    months: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get revenue data over time for charts."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    results = db.query(
        extract('year', SalesRecord.actual_close_date).label('year'),
        extract('month', SalesRecord.actual_close_date).label('month'),
        func.sum(SalesRecord.amount).label('revenue')
    ).filter(
        SalesRecord.stage == DealStage.CLOSED_WON,
        SalesRecord.actual_close_date >= start_date,
        SalesRecord.actual_close_date <= end_date
    ).group_by(
        extract('year', SalesRecord.actual_close_date),
        extract('month', SalesRecord.actual_close_date)
    ).order_by('year', 'month').all()
    
    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "revenue": round(r.revenue, 2)
        }
        for r in results
    ]


@router.get("/lead-funnel")
def get_lead_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead conversion funnel data."""
    funnel_stages = [
        LeadStatus.NEW,
        LeadStatus.CONTACTED,
        LeadStatus.QUALIFIED,
        LeadStatus.PROPOSAL,
        LeadStatus.NEGOTIATION,
        LeadStatus.CLOSED_WON
    ]
    
    funnel_data = []
    for stage in funnel_stages:
        count = db.query(func.count(Lead.id)).filter(Lead.status == stage).scalar() or 0
        funnel_data.append({
            "stage": stage.value,
            "count": count
        })
    
    return funnel_data


@router.get("/campaign-performance")
def get_campaign_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign performance summary."""
    campaigns = db.query(Campaign).filter(
        Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.COMPLETED])
    ).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "type": c.campaign_type.value,
            "status": c.status.value,
            "budget": c.budget,
            "spent": c.spent,
            "impressions": c.impressions,
            "clicks": c.clicks,
            "conversions": c.conversions,
            "leads_generated": c.leads_generated,
            "roi": c.roi,
            "click_through_rate": c.click_through_rate,
            "conversion_rate": c.conversion_rate
        }
        for c in campaigns
    ]


@router.get("/sales-by-rep")
def get_sales_by_rep(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sales performance by representative."""
    results = db.query(
        User.id,
        User.full_name,
        func.count(SalesRecord.id).label('deals_count'),
        func.sum(SalesRecord.amount).label('total_revenue')
    ).join(SalesRecord, User.id == SalesRecord.sales_rep_id).filter(
        SalesRecord.stage == DealStage.CLOSED_WON
    ).group_by(User.id, User.full_name).all()
    
    return [
        {
            "id": r.id,
            "name": r.full_name,
            "deals_count": r.deals_count,
            "total_revenue": round(r.total_revenue or 0, 2)
        }
        for r in results
    ]


@router.get("/lead-sources")
def get_lead_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead distribution by source."""
    results = db.query(
        Lead.source,
        func.count(Lead.id).label('count')
    ).group_by(Lead.source).all()
    
    return [
        {
            "source": r.source.value,
            "count": r.count
        }
        for r in results
    ]

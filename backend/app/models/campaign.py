from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    PPC = "ppc"
    CONTENT = "content"
    EVENT = "event"
    WEBINAR = "webinar"
    OTHER = "other"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    campaign_type = Column(Enum(CampaignType), default=CampaignType.EMAIL)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Target audience
    target_audience = Column(String(255))
    target_industry = Column(String(100))
    
    # Budget and costs
    budget = Column(Float, default=0)
    spent = Column(Float, default=0)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    revenue_attributed = Column(Float, default=0)
    
    # Calculated metrics (stored for quick access)
    click_through_rate = Column(Float, default=0)  # clicks / impressions
    conversion_rate = Column(Float, default=0)  # conversions / clicks
    cost_per_lead = Column(Float, default=0)  # spent / leads_generated
    roi = Column(Float, default=0)  # (revenue - spent) / spent
    
    # Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Content (for RAG)
    content = Column(Text)  # Marketing copy, messages, etc.
    
    # Creator
    created_by = Column(Integer, ForeignKey("users.id"))
    created_by_user = relationship("User", back_populates="campaigns")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_metrics(self):
        """Recalculate derived metrics."""
        if self.impressions > 0:
            self.click_through_rate = (self.clicks / self.impressions) * 100
        if self.clicks > 0:
            self.conversion_rate = (self.conversions / self.clicks) * 100
        if self.leads_generated > 0:
            self.cost_per_lead = self.spent / self.leads_generated
        if self.spent > 0:
            self.roi = ((self.revenue_attributed - self.spent) / self.spent) * 100

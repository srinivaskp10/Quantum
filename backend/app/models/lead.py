from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    COLD_CALL = "cold_call"
    EMAIL_CAMPAIGN = "email_campaign"
    TRADE_SHOW = "trade_show"
    OTHER = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    job_title = Column(String(255))
    
    # Lead details
    industry = Column(String(100), index=True)
    company_size = Column(String(50))  # e.g., "1-10", "11-50", "51-200", etc.
    annual_revenue = Column(Float)  # Estimated annual revenue
    location = Column(String(255))
    
    # Lead status and scoring
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    source = Column(Enum(LeadSource), default=LeadSource.OTHER)
    
    # AI scoring fields
    ai_score = Column(Float)  # 0-100 score
    ai_score_reasoning = Column(Text)  # AI explanation
    ai_score_updated_at = Column(DateTime)
    
    # Expected deal value
    estimated_value = Column(Float)
    
    # Notes and context (for RAG)
    notes = Column(Text)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_to_user = relationship("User", back_populates="leads")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_date = Column(DateTime)

    # Relationship to customer (if converted)
    customer = relationship("Customer", back_populates="lead", uselist=False)

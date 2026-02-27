from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class DealStage(str, enum.Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Related entities
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="sales_records")
    
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    sales_rep = relationship("User", back_populates="sales_records")
    
    # Deal details
    deal_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Financials
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    # Stage tracking
    stage = Column(Enum(DealStage), default=DealStage.PROSPECTING, index=True)
    probability = Column(Float, default=0)  # Win probability percentage
    
    # Product/Service info
    product_name = Column(String(255))
    quantity = Column(Integer, default=1)
    
    # Timeline
    close_date = Column(DateTime)
    actual_close_date = Column(DateTime)
    
    # Notes (for RAG)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

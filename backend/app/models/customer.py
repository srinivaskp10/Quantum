from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Converted from lead
    lead_id = Column(Integer, ForeignKey("leads.id"), unique=True)
    lead = relationship("Lead", back_populates="customer")
    
    # Company information
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    
    # Business details
    industry = Column(String(100))
    company_size = Column(String(50))
    location = Column(String(255))
    
    # Customer metrics
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    lifetime_value = Column(Float, default=0)
    total_purchases = Column(Integer, default=0)
    
    # Account details
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales_records = relationship("SalesRecord", back_populates="customer")

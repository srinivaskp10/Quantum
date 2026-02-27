from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.customer import CustomerStatus


class CustomerBase(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    lead_id: Optional[int] = None
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None


class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    status: Optional[CustomerStatus] = None
    notes: Optional[str] = None
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None


class CustomerResponse(CustomerBase):
    id: int
    lead_id: Optional[int] = None
    status: CustomerStatus
    lifetime_value: float
    total_purchases: int
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

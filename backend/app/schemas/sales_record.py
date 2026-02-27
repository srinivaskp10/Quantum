from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.sales_record import DealStage


class SalesRecordBase(BaseModel):
    deal_name: str
    description: Optional[str] = None
    amount: float
    currency: str = "USD"
    product_name: Optional[str] = None
    quantity: int = 1
    notes: Optional[str] = None


class SalesRecordCreate(SalesRecordBase):
    customer_id: int
    stage: DealStage = DealStage.PROSPECTING
    probability: float = 0
    close_date: Optional[datetime] = None


class SalesRecordUpdate(BaseModel):
    deal_name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    stage: Optional[DealStage] = None
    probability: Optional[float] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    notes: Optional[str] = None


class SalesRecordResponse(SalesRecordBase):
    id: int
    customer_id: int
    sales_rep_id: Optional[int] = None
    stage: DealStage
    probability: float
    close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

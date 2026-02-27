from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.sales_record import SalesRecord, DealStage
from app.models.customer import Customer
from app.schemas.sales_record import SalesRecordCreate, SalesRecordUpdate, SalesRecordResponse

router = APIRouter()


@router.get("/", response_model=List[SalesRecordResponse])
def list_sales_records(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[DealStage] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sales records with optional filters."""
    query = db.query(SalesRecord)
    
    # Sales users can only see their own records
    if current_user.role == UserRole.SALES:
        query = query.filter(SalesRecord.sales_rep_id == current_user.id)
    
    if stage:
        query = query.filter(SalesRecord.stage == stage)
    if customer_id:
        query = query.filter(SalesRecord.customer_id == customer_id)
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.post("/", response_model=SalesRecordResponse, status_code=status.HTTP_201_CREATED)
def create_sales_record(
    record_data: SalesRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sales record."""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == record_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    record = SalesRecord(**record_data.model_dump())
    record.sales_rep_id = current_user.id
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=SalesRecordResponse)
def get_sales_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sales record."""
    record = db.query(SalesRecord).filter(SalesRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales record not found"
        )
    
    if current_user.role == UserRole.SALES and record.sales_rep_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this record"
        )
    
    return record


@router.put("/{record_id}", response_model=SalesRecordResponse)
def update_sales_record(
    record_id: int,
    record_data: SalesRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sales record."""
    record = db.query(SalesRecord).filter(SalesRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales record not found"
        )
    
    if current_user.role == UserRole.SALES and record.sales_rep_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this record"
        )
    
    update_data = record_data.model_dump(exclude_unset=True)
    
    # If stage changes to closed_won, set actual close date
    if 'stage' in update_data and update_data['stage'] == DealStage.CLOSED_WON:
        record.actual_close_date = datetime.utcnow()
        # Update customer lifetime value
        if record.customer:
            record.customer.lifetime_value += record.amount
            record.customer.total_purchases += 1
    
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sales_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sales record."""
    record = db.query(SalesRecord).filter(SalesRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales record not found"
        )
    
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete sales records"
        )
    
    db.delete(record)
    db.commit()
    return None

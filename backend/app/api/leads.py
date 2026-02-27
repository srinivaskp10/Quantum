from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus, LeadSource
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse

router = APIRouter()


@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List leads with optional filters."""
    query = db.query(Lead)
    
    # Sales users can only see their assigned leads
    if current_user.role == UserRole.SALES:
        query = query.filter(Lead.assigned_to == current_user.id)
    
    if status:
        query = query.filter(Lead.status == status)
    if source:
        query = query.filter(Lead.source == source)
    if industry:
        query = query.filter(Lead.industry.ilike(f"%{industry}%"))
    
    leads = query.offset(skip).limit(limit).all()
    return leads


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lead."""
    lead = Lead(**lead_data.model_dump())
    
    # Auto-assign to current user if not specified
    if lead.assigned_to is None:
        lead.assigned_to = current_user.id
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check access for sales users
    if current_user.role == UserRole.SALES and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this lead"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    if current_user.role == UserRole.SALES and lead.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lead"
        )
    
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.MARKETING]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete leads"
        )
    
    db.delete(lead)
    db.commit()
    return None


@router.post("/upload-csv", response_model=dict)
async def upload_leads_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload leads from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    required_columns = ['company_name', 'contact_name', 'email']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {missing_columns}"
        )
    
    created_count = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Map source string to enum
            source = LeadSource.OTHER
            if 'source' in row and pd.notna(row['source']):
                try:
                    source = LeadSource(row['source'].lower())
                except ValueError:
                    source = LeadSource.OTHER
            
            lead = Lead(
                company_name=row['company_name'],
                contact_name=row['contact_name'],
                email=row['email'],
                phone=row.get('phone') if pd.notna(row.get('phone')) else None,
                job_title=row.get('job_title') if pd.notna(row.get('job_title')) else None,
                industry=row.get('industry') if pd.notna(row.get('industry')) else None,
                company_size=row.get('company_size') if pd.notna(row.get('company_size')) else None,
                annual_revenue=float(row['annual_revenue']) if pd.notna(row.get('annual_revenue')) else None,
                location=row.get('location') if pd.notna(row.get('location')) else None,
                source=source,
                estimated_value=float(row['estimated_value']) if pd.notna(row.get('estimated_value')) else None,
                notes=row.get('notes') if pd.notna(row.get('notes')) else None,
                assigned_to=current_user.id
            )
            db.add(lead)
            created_count += 1
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    db.commit()
    
    return {
        "message": f"Successfully uploaded {created_count} leads",
        "created_count": created_count,
        "errors": errors
    }

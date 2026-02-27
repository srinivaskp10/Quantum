from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from pgvector.sqlalchemy import Vector
from datetime import datetime
import enum
from app.core.database import Base
from app.core.config import settings


class DocumentType(str, enum.Enum):
    LEAD_NOTE = "lead_note"
    CUSTOMER_NOTE = "customer_note"
    CAMPAIGN_CONTENT = "campaign_content"
    SALES_NOTE = "sales_note"
    INSIGHT = "insight"


class VectorDocument(Base):
    """Store documents with vector embeddings for semantic search (RAG)."""
    __tablename__ = "vector_documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # Document content
    content = Column(Text, nullable=False)
    
    # Document metadata
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    source_id = Column(Integer, index=True)  # ID of the source entity (lead, customer, etc.)
    source_table = Column(String(50))  # Name of the source table
    
    # Vector embedding (1536 dimensions for OpenAI embeddings)
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    # Additional metadata
    doc_metadata = Column(Text)  # JSON string for flexible metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

from typing import List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.vector_store import VectorDocument, DocumentType
from app.services.openai_client import openai_service
from app.core.config import settings


class VectorStoreService:
    """Service for storing and searching documents using pgvector."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_document(
        self,
        content: str,
        document_type: DocumentType,
        source_id: int,
        source_table: str,
        metadata: Optional[dict] = None
    ) -> VectorDocument:
        """Add a document to the vector store with its embedding."""
        embedding = openai_service.create_embedding(content)
        
        doc = VectorDocument(
            content=content,
            document_type=document_type,
            source_id=source_id,
            source_table=source_table,
            embedding=embedding,
            doc_metadata=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc
    
    def add_documents_batch(
        self,
        documents: List[dict]
    ) -> List[VectorDocument]:
        """Add multiple documents efficiently."""
        contents = [d['content'] for d in documents]
        embeddings = openai_service.create_embeddings_batch(contents)
        
        created_docs = []
        for doc_data, embedding in zip(documents, embeddings):
            doc = VectorDocument(
                content=doc_data['content'],
                document_type=doc_data['document_type'],
                source_id=doc_data['source_id'],
                source_table=doc_data['source_table'],
                embedding=embedding,
                doc_metadata=json.dumps(doc_data.get('metadata')) if doc_data.get('metadata') else None
            )
            self.db.add(doc)
            created_docs.append(doc)
        
        self.db.commit()
        for doc in created_docs:
            self.db.refresh(doc)
        
        return created_docs
    
    def search(
        self,
        query: str,
        document_type: Optional[DocumentType] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[dict]:
        """Search for similar documents using cosine similarity."""
        query_embedding = openai_service.create_embedding(query)
        
        # Build the query with pgvector cosine similarity
        base_query = """
            SELECT 
                id, content, document_type, source_id, source_table, doc_metadata,
                1 - (embedding <=> :embedding::vector) as similarity
            FROM vector_documents
            WHERE 1 - (embedding <=> :embedding::vector) > :threshold
        """
        
        if document_type:
            base_query += " AND document_type = :doc_type"
        
        base_query += " ORDER BY embedding <=> :embedding::vector LIMIT :limit"
        
        params = {
            "embedding": str(query_embedding),
            "threshold": similarity_threshold,
            "limit": limit
        }
        
        if document_type:
            params["doc_type"] = document_type.value
        
        result = self.db.execute(text(base_query), params)
        
        results = []
        for row in result:
            results.append({
                "id": row.id,
                "content": row.content,
                "document_type": row.document_type,
                "source_id": row.source_id,
                "source_table": row.source_table,
                "metadata": json.loads(row.doc_metadata) if row.doc_metadata else None,
                "similarity": round(row.similarity, 4)
            })
        
        return results
    
    def get_context_for_prompt(
        self,
        query: str,
        document_type: Optional[DocumentType] = None,
        max_tokens: int = 2000
    ) -> str:
        """Get relevant context for RAG prompt injection."""
        results = self.search(query, document_type, limit=10)
        
        if not results:
            return ""
        
        context_parts = []
        current_tokens = 0
        
        for result in results:
            content = result['content']
            # Rough token estimation (1 token ≈ 4 chars)
            content_tokens = len(content) // 4
            
            if current_tokens + content_tokens > max_tokens:
                break
            
            context_parts.append(f"[{result['document_type']}] {content}")
            current_tokens += content_tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def update_document(
        self,
        document_id: int,
        content: str
    ) -> Optional[VectorDocument]:
        """Update a document's content and embedding."""
        doc = self.db.query(VectorDocument).filter(VectorDocument.id == document_id).first()
        if not doc:
            return None
        
        doc.content = content
        doc.embedding = openai_service.create_embedding(content)
        
        self.db.commit()
        self.db.refresh(doc)
        return doc
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document from the vector store."""
        doc = self.db.query(VectorDocument).filter(VectorDocument.id == document_id).first()
        if not doc:
            return False
        
        self.db.delete(doc)
        self.db.commit()
        return True
    
    def delete_by_source(self, source_table: str, source_id: int) -> int:
        """Delete all documents from a specific source."""
        deleted = self.db.query(VectorDocument).filter(
            VectorDocument.source_table == source_table,
            VectorDocument.source_id == source_id
        ).delete()
        self.db.commit()
        return deleted
    
    def index_lead_notes(self, lead_id: int, notes: str):
        """Index lead notes for RAG."""
        if not notes:
            return
        
        # Delete existing
        self.delete_by_source("leads", lead_id)
        
        # Add new
        self.add_document(
            content=notes,
            document_type=DocumentType.LEAD_NOTE,
            source_id=lead_id,
            source_table="leads"
        )
    
    def index_campaign_content(self, campaign_id: int, content: str, description: str = ""):
        """Index campaign content for RAG."""
        full_content = f"{description}\n\n{content}".strip()
        if not full_content:
            return
        
        self.delete_by_source("campaigns", campaign_id)
        
        self.add_document(
            content=full_content,
            document_type=DocumentType.CAMPAIGN_CONTENT,
            source_id=campaign_id,
            source_table="campaigns"
        )
    
    def index_sales_notes(self, record_id: int, notes: str):
        """Index sales record notes for RAG."""
        if not notes:
            return
        
        self.delete_by_source("sales_records", record_id)
        
        self.add_document(
            content=notes,
            document_type=DocumentType.SALES_NOTE,
            source_id=record_id,
            source_table="sales_records"
        )

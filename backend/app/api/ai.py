from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.lead_scoring import LeadScoringService
from app.services.chat_agent import ChatAgentService
from app.services.content_generator import ContentGeneratorService
from app.services.insights_generator import InsightsGeneratorService
from app.services.vector_store import VectorStoreService
from app.schemas.ai import (
    LeadScoreRequest, LeadScoreResponse,
    ChatRequest, ChatResponse,
    ContentGenerateRequest, ContentGenerateResponse,
    InsightRequest, InsightResponse,
    SemanticSearchRequest, SemanticSearchResponse
)
from app.models.vector_store import DocumentType

router = APIRouter()


@router.post("/score-lead", response_model=LeadScoreResponse)
def score_lead(
    request: LeadScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Score a lead using AI analysis."""
    try:
        service = LeadScoringService(db)
        return service.score_lead(request.lead_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI scoring failed: {str(e)}"
        )


@router.post("/score-leads-batch", response_model=List[LeadScoreResponse])
def score_leads_batch(
    lead_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Score multiple leads using AI analysis."""
    service = LeadScoringService(db)
    results = service.batch_score_leads(lead_ids)
    return results


@router.post("/chat", response_model=ChatResponse)
def chat_with_data(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conversational interface to query sales data using natural language."""
    try:
        service = ChatAgentService(db)
        return service.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/generate-content", response_model=ContentGenerateResponse)
def generate_marketing_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate marketing content variations using AI."""
    try:
        service = ContentGeneratorService()
        return service.generate_content(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/generate-email-sequence")
def generate_email_sequence(
    target_audience: str,
    industry: str,
    campaign_goal: str,
    num_emails: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate an email nurture sequence using AI."""
    try:
        service = ContentGeneratorService()
        return service.generate_email_sequence(
            target_audience=target_audience,
            industry=industry,
            campaign_goal=campaign_goal,
            num_emails=num_emails
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email sequence generation failed: {str(e)}"
        )


@router.post("/insights", response_model=InsightResponse)
def generate_insights(
    request: InsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered business insights."""
    try:
        service = InsightsGeneratorService(db)
        return service.generate_insight(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insight generation failed: {str(e)}"
        )


@router.post("/semantic-search", response_model=SemanticSearchResponse)
def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search documents using semantic similarity."""
    try:
        service = VectorStoreService(db)
        document_type = DocumentType(request.document_type) if request.document_type else None
        results = service.search(
            query=request.query,
            document_type=document_type,
            limit=request.limit
        )
        return SemanticSearchResponse(results=results, query=request.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/rag-query")
def rag_enhanced_query(
    query: str,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Query with RAG-enhanced context retrieval."""
    try:
        vector_service = VectorStoreService(db)
        doc_type = DocumentType(document_type) if document_type else None
        
        # Get relevant context
        context = vector_service.get_context_for_prompt(
            query=query,
            document_type=doc_type
        )
        
        # Use chat agent with enhanced context
        chat_service = ChatAgentService(db)
        
        enhanced_message = query
        if context:
            enhanced_message = f"""Using the following context from our knowledge base:

{context}

---

Answer this question: {query}"""
        
        return chat_service.process_message(enhanced_message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )


@router.get("/insight-types")
def get_insight_types(
    current_user: User = Depends(get_current_user)
):
    """Get available insight types."""
    return {
        "insight_types": [
            {
                "id": "weekly_sales",
                "name": "Weekly Sales Summary",
                "description": "AI-generated summary of weekly sales performance"
            },
            {
                "id": "campaign_performance",
                "name": "Campaign Performance",
                "description": "Analysis of marketing campaign effectiveness"
            },
            {
                "id": "revenue_forecast",
                "name": "Revenue Forecast",
                "description": "Predictive revenue forecast for next quarter"
            },
            {
                "id": "lead_analysis",
                "name": "Lead Funnel Analysis",
                "description": "Analysis of lead sources and conversion funnel"
            }
        ]
    }

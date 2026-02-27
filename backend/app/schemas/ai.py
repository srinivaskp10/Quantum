from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LeadScoreRequest(BaseModel):
    lead_id: int


class LeadScoreResponse(BaseModel):
    lead_id: int
    score: float = Field(..., ge=0, le=100)
    probability: float = Field(..., ge=0, le=1)
    reasoning: str
    factors: List[str]
    recommendations: List[str]


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sql_query: Optional[str] = None
    data: Optional[List[dict]] = None
    conversation_id: str


class ContentGenerateRequest(BaseModel):
    target_audience: str
    industry: str
    tone: str = Field(..., description="e.g., professional, casual, persuasive")
    platform: str = Field(..., description="e.g., LinkedIn, Email, Twitter, Blog")
    topic: Optional[str] = None
    key_points: Optional[List[str]] = None
    max_length: Optional[int] = None


class ContentGenerateResponse(BaseModel):
    variations: List[str]
    platform: str
    tone: str
    metadata: dict


class InsightRequest(BaseModel):
    insight_type: str = Field(..., description="weekly_sales, campaign_performance, revenue_forecast")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class InsightResponse(BaseModel):
    insight_type: str
    title: str
    summary: str
    key_metrics: dict
    recommendations: List[str]
    generated_at: datetime


class SemanticSearchRequest(BaseModel):
    query: str
    document_type: Optional[str] = None
    limit: int = 5


class SemanticSearchResponse(BaseModel):
    results: List[dict]
    query: str

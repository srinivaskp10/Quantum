from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.services.openai_client import openai_service
from app.schemas.ai import LeadScoreResponse


class LeadScoringService:
    """AI-powered lead scoring using OpenAI."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def score_lead(self, lead_id: int) -> LeadScoreResponse:
        """Score a lead using AI analysis."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead with id {lead_id} not found")
        
        # Build context about the lead
        lead_context = self._build_lead_context(lead)
        
        # Create the scoring prompt
        messages = [
            {
                "role": "system",
                "content": """You are an expert sales analyst. Your task is to score leads based on their 
potential to convert into customers. Analyze the provided lead information and return a JSON response with:
- score: A number from 0 to 100 representing conversion likelihood
- probability: A decimal from 0 to 1 representing conversion probability
- reasoning: A brief explanation of your scoring rationale
- factors: An array of positive and negative factors affecting the score
- recommendations: An array of actionable recommendations for the sales team

Consider factors like:
- Company size and revenue (larger companies often mean bigger deals)
- Industry fit (some industries convert better)
- Job title seniority (decision makers score higher)
- Lead source quality
- Engagement indicators (notes, interactions)
- Estimated deal value"""
            },
            {
                "role": "user",
                "content": f"""Please score this lead:

{lead_context}

Return your analysis as a JSON object with keys: score, probability, reasoning, factors, recommendations"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.3)
        
        # Update the lead with AI score
        lead.ai_score = result.get('score', 0)
        lead.ai_score_reasoning = result.get('reasoning', '')
        lead.ai_score_updated_at = datetime.utcnow()
        self.db.commit()
        
        return LeadScoreResponse(
            lead_id=lead_id,
            score=result.get('score', 0),
            probability=result.get('probability', 0),
            reasoning=result.get('reasoning', ''),
            factors=result.get('factors', []),
            recommendations=result.get('recommendations', [])
        )
    
    def _build_lead_context(self, lead: Lead) -> str:
        """Build a context string from lead attributes."""
        context_parts = [
            f"Company: {lead.company_name}",
            f"Contact: {lead.contact_name}",
            f"Job Title: {lead.job_title or 'Unknown'}",
            f"Industry: {lead.industry or 'Unknown'}",
            f"Company Size: {lead.company_size or 'Unknown'}",
            f"Annual Revenue: ${lead.annual_revenue:,.0f}" if lead.annual_revenue else "Annual Revenue: Unknown",
            f"Location: {lead.location or 'Unknown'}",
            f"Lead Source: {lead.source.value}",
            f"Current Status: {lead.status.value}",
            f"Estimated Deal Value: ${lead.estimated_value:,.0f}" if lead.estimated_value else "Estimated Value: Unknown",
            f"Notes: {lead.notes}" if lead.notes else "Notes: None"
        ]
        return "\n".join(context_parts)
    
    def batch_score_leads(self, lead_ids: list) -> list:
        """Score multiple leads."""
        results = []
        for lead_id in lead_ids:
            try:
                result = self.score_lead(lead_id)
                results.append(result)
            except Exception as e:
                results.append({
                    "lead_id": lead_id,
                    "error": str(e)
                })
        return results

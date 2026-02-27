from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.lead import Lead, LeadStatus
from app.models.customer import Customer
from app.models.campaign import Campaign, CampaignStatus
from app.models.sales_record import SalesRecord, DealStage
from app.services.openai_client import openai_service
from app.schemas.ai import InsightRequest, InsightResponse


class InsightsGeneratorService:
    """AI-powered business insights generation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_insight(self, request: InsightRequest) -> InsightResponse:
        """Generate insights based on the requested type."""
        insight_generators = {
            "weekly_sales": self._generate_weekly_sales_summary,
            "campaign_performance": self._generate_campaign_performance_summary,
            "revenue_forecast": self._generate_revenue_forecast,
            "lead_analysis": self._generate_lead_analysis
        }
        
        generator = insight_generators.get(request.insight_type)
        if not generator:
            raise ValueError(f"Unknown insight type: {request.insight_type}")
        
        return generator(request.start_date, request.end_date)
    
    def _generate_weekly_sales_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> InsightResponse:
        """Generate weekly sales summary with AI insights."""
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=7))
        
        # Gather sales data
        closed_deals = self.db.query(SalesRecord).filter(
            SalesRecord.stage == DealStage.CLOSED_WON,
            SalesRecord.actual_close_date >= start_date,
            SalesRecord.actual_close_date <= end_date
        ).all()
        
        lost_deals = self.db.query(SalesRecord).filter(
            SalesRecord.stage == DealStage.CLOSED_LOST,
            SalesRecord.updated_at >= start_date,
            SalesRecord.updated_at <= end_date
        ).all()
        
        total_revenue = sum(d.amount for d in closed_deals)
        avg_deal_size = total_revenue / len(closed_deals) if closed_deals else 0
        win_rate = len(closed_deals) / (len(closed_deals) + len(lost_deals)) * 100 if (closed_deals or lost_deals) else 0
        
        # New leads this week
        new_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.created_at >= start_date,
            Lead.created_at <= end_date
        ).scalar() or 0
        
        # Build context for AI
        context = f"""
Weekly Sales Data ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}):
- Deals Closed: {len(closed_deals)}
- Total Revenue: ${total_revenue:,.2f}
- Average Deal Size: ${avg_deal_size:,.2f}
- Deals Lost: {len(lost_deals)}
- Win Rate: {win_rate:.1f}%
- New Leads: {new_leads}

Top deals closed:
{chr(10).join([f'- {d.deal_name}: ${d.amount:,.2f}' for d in sorted(closed_deals, key=lambda x: x.amount, reverse=True)[:5]])}
"""
        
        # Generate AI insights
        messages = [
            {
                "role": "system",
                "content": """You are a senior sales analyst. Analyze the weekly sales data and provide 
actionable insights. Focus on trends, opportunities, and recommendations."""
            },
            {
                "role": "user",
                "content": f"""{context}

Provide a JSON response with:
- title: A compelling title for this week's summary
- summary: 2-3 paragraph executive summary
- highlights: Array of 3-5 key highlights
- concerns: Array of any concerns or areas needing attention
- recommendations: Array of 3-5 actionable recommendations for next week"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.5)
        
        return InsightResponse(
            insight_type="weekly_sales",
            title=result.get('title', 'Weekly Sales Summary'),
            summary=result.get('summary', ''),
            key_metrics={
                "total_revenue": total_revenue,
                "deals_closed": len(closed_deals),
                "deals_lost": len(lost_deals),
                "win_rate": win_rate,
                "avg_deal_size": avg_deal_size,
                "new_leads": new_leads,
                "highlights": result.get('highlights', []),
                "concerns": result.get('concerns', [])
            },
            recommendations=result.get('recommendations', []),
            generated_at=datetime.utcnow()
        )
    
    def _generate_campaign_performance_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> InsightResponse:
        """Generate campaign performance summary with AI insights."""
        campaigns = self.db.query(Campaign).filter(
            Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.COMPLETED])
        ).all()
        
        total_spent = sum(c.spent for c in campaigns)
        total_revenue = sum(c.revenue_attributed for c in campaigns)
        total_leads = sum(c.leads_generated for c in campaigns)
        avg_roi = sum(c.roi for c in campaigns) / len(campaigns) if campaigns else 0
        
        context = f"""
Campaign Performance Summary:
- Active/Completed Campaigns: {len(campaigns)}
- Total Budget Spent: ${total_spent:,.2f}
- Total Revenue Attributed: ${total_revenue:,.2f}
- Overall ROI: {((total_revenue - total_spent) / total_spent * 100) if total_spent else 0:.1f}%
- Total Leads Generated: {total_leads}
- Average Cost Per Lead: ${total_spent / total_leads if total_leads else 0:.2f}

Individual Campaign Performance:
{chr(10).join([f'- {c.name}: ROI {c.roi:.1f}%, {c.leads_generated} leads, ${c.spent:,.2f} spent' for c in sorted(campaigns, key=lambda x: x.roi, reverse=True)[:10]])}
"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a marketing analytics expert. Analyze campaign performance data 
and provide strategic insights for optimization."""
            },
            {
                "role": "user",
                "content": f"""{context}

Provide a JSON response with:
- title: Compelling title for this report
- summary: Executive summary of campaign performance
- top_performers: Analysis of best performing campaigns and why
- underperformers: Campaigns that need attention and suggested fixes
- recommendations: Strategic recommendations for campaign optimization"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.5)
        
        return InsightResponse(
            insight_type="campaign_performance",
            title=result.get('title', 'Campaign Performance Summary'),
            summary=result.get('summary', ''),
            key_metrics={
                "total_campaigns": len(campaigns),
                "total_spent": total_spent,
                "total_revenue": total_revenue,
                "total_leads": total_leads,
                "average_roi": avg_roi,
                "top_performers": result.get('top_performers', ''),
                "underperformers": result.get('underperformers', '')
            },
            recommendations=result.get('recommendations', []) if isinstance(result.get('recommendations'), list) else [result.get('recommendations', '')],
            generated_at=datetime.utcnow()
        )
    
    def _generate_revenue_forecast(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> InsightResponse:
        """Generate revenue forecast for next quarter."""
        # Historical data for last 6 months
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        historical_sales = self.db.query(
            func.date_trunc('month', SalesRecord.actual_close_date).label('month'),
            func.sum(SalesRecord.amount).label('revenue')
        ).filter(
            SalesRecord.stage == DealStage.CLOSED_WON,
            SalesRecord.actual_close_date >= six_months_ago
        ).group_by('month').order_by('month').all()
        
        # Pipeline value
        pipeline = self.db.query(SalesRecord).filter(
            SalesRecord.stage.not_in([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        ).all()
        
        pipeline_value = sum(d.amount * (d.probability / 100) for d in pipeline)
        
        historical_str = "\n".join([
            f"- {h.month.strftime('%Y-%m') if h.month else 'Unknown'}: ${h.revenue:,.2f}"
            for h in historical_sales
        ])
        
        context = f"""
Historical Monthly Revenue (Last 6 months):
{historical_str}

Current Pipeline:
- Total Pipeline Value: ${sum(d.amount for d in pipeline):,.2f}
- Weighted Pipeline (by probability): ${pipeline_value:,.2f}
- Open Deals: {len(pipeline)}
"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a financial analyst specializing in revenue forecasting. 
Analyze historical trends and pipeline data to forecast next quarter's revenue."""
            },
            {
                "role": "user",
                "content": f"""{context}

Provide a JSON response with:
- title: Report title
- summary: Executive summary of the forecast
- forecast_low: Conservative revenue estimate for next quarter
- forecast_mid: Most likely revenue estimate
- forecast_high: Optimistic revenue estimate
- confidence_level: Your confidence in this forecast (low/medium/high)
- key_assumptions: Assumptions underlying this forecast
- risks: Potential risks to the forecast
- recommendations: Actions to improve revenue performance"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.4)
        
        return InsightResponse(
            insight_type="revenue_forecast",
            title=result.get('title', 'Quarterly Revenue Forecast'),
            summary=result.get('summary', ''),
            key_metrics={
                "forecast_low": result.get('forecast_low', 0),
                "forecast_mid": result.get('forecast_mid', 0),
                "forecast_high": result.get('forecast_high', 0),
                "confidence_level": result.get('confidence_level', 'medium'),
                "pipeline_value": pipeline_value,
                "open_deals": len(pipeline),
                "key_assumptions": result.get('key_assumptions', []),
                "risks": result.get('risks', [])
            },
            recommendations=result.get('recommendations', []) if isinstance(result.get('recommendations'), list) else [result.get('recommendations', '')],
            generated_at=datetime.utcnow()
        )
    
    def _generate_lead_analysis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> InsightResponse:
        """Generate lead funnel analysis."""
        leads = self.db.query(Lead).all()
        
        status_counts = {}
        for lead in leads:
            status = lead.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_score = sum(l.ai_score or 0 for l in leads) / len(leads) if leads else 0
        high_score_leads = [l for l in leads if (l.ai_score or 0) >= 70]
        
        by_source = {}
        for lead in leads:
            source = lead.source.value
            by_source[source] = by_source.get(source, 0) + 1
        
        context = f"""
Lead Analysis:
- Total Leads: {len(leads)}
- Average AI Score: {avg_score:.1f}
- High-Scoring Leads (70+): {len(high_score_leads)}

Lead Status Distribution:
{chr(10).join([f'- {k}: {v}' for k, v in status_counts.items()])}

Lead Sources:
{chr(10).join([f'- {k}: {v}' for k, v in sorted(by_source.items(), key=lambda x: x[1], reverse=True)])}
"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a sales operations analyst. Analyze lead data to identify 
patterns, bottlenecks, and opportunities for improvement."""
            },
            {
                "role": "user",
                "content": f"""{context}

Provide a JSON response with:
- title: Report title
- summary: Key findings summary
- funnel_analysis: Analysis of the lead funnel health
- source_analysis: Which lead sources are performing best/worst
- recommendations: Specific actions to improve lead quality and conversion"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.5)
        
        return InsightResponse(
            insight_type="lead_analysis",
            title=result.get('title', 'Lead Funnel Analysis'),
            summary=result.get('summary', ''),
            key_metrics={
                "total_leads": len(leads),
                "avg_ai_score": avg_score,
                "high_score_count": len(high_score_leads),
                "status_distribution": status_counts,
                "source_distribution": by_source,
                "funnel_analysis": result.get('funnel_analysis', ''),
                "source_analysis": result.get('source_analysis', '')
            },
            recommendations=result.get('recommendations', []) if isinstance(result.get('recommendations'), list) else [result.get('recommendations', '')],
            generated_at=datetime.utcnow()
        )

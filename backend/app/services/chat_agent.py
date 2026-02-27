import re
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.openai_client import openai_service
from app.schemas.ai import ChatResponse


class ChatAgentService:
    """Conversational agent that converts natural language to SQL queries."""
    
    # Allowed tables for querying (security whitelist)
    ALLOWED_TABLES = ['leads', 'customers', 'campaigns', 'sales_records', 'users']
    
    # Database schema context for the LLM
    SCHEMA_CONTEXT = """
    Database Schema:
    
    1. users (id, email, full_name, role, is_active, created_at)
       - role can be: 'admin', 'sales', 'marketing'
    
    2. leads (id, company_name, contact_name, email, phone, job_title, industry, 
              company_size, annual_revenue, location, status, source, ai_score, 
              estimated_value, notes, assigned_to, created_at, last_contact_date)
       - status: 'new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
       - source: 'website', 'referral', 'linkedin', 'cold_call', 'email_campaign', 'trade_show', 'other'
    
    3. customers (id, lead_id, company_name, contact_name, email, phone, industry,
                  company_size, location, status, lifetime_value, total_purchases, created_at)
       - status: 'active', 'inactive', 'churned'
    
    4. campaigns (id, name, description, campaign_type, status, target_audience, target_industry,
                  budget, spent, impressions, clicks, conversions, leads_generated, revenue_attributed,
                  click_through_rate, conversion_rate, cost_per_lead, roi, start_date, end_date)
       - campaign_type: 'email', 'social_media', 'ppc', 'content', 'event', 'webinar', 'other'
       - status: 'draft', 'active', 'paused', 'completed', 'cancelled'
    
    5. sales_records (id, customer_id, sales_rep_id, deal_name, description, amount, currency,
                      stage, probability, product_name, quantity, close_date, actual_close_date, notes)
       - stage: 'prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.conversations: Dict[str, List[dict]] = {}
    
    def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        """Process a natural language message and return data insights."""
        
        # Generate or retrieve conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Get conversation history
        history = self.conversations.get(conversation_id, [])
        
        # Generate SQL query from natural language
        sql_query = self._generate_sql(message, history)
        
        # Validate SQL for security
        if not self._validate_sql(sql_query):
            return ChatResponse(
                answer="I can only help with data queries. Please ask about your sales, leads, campaigns, or customers.",
                sql_query=None,
                data=None,
                conversation_id=conversation_id
            )
        
        # Execute the query safely
        try:
            data = self._execute_query(sql_query)
        except Exception as e:
            return ChatResponse(
                answer=f"I encountered an error processing your request. Please try rephrasing your question.",
                sql_query=sql_query,
                data=None,
                conversation_id=conversation_id
            )
        
        # Generate natural language response
        answer = self._generate_response(message, sql_query, data)
        
        # Update conversation history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        self.conversations[conversation_id] = history[-10:]  # Keep last 10 messages
        
        return ChatResponse(
            answer=answer,
            sql_query=sql_query,
            data=data[:100] if data else None,  # Limit returned data
            conversation_id=conversation_id
        )
    
    def _generate_sql(self, message: str, history: List[dict]) -> str:
        """Convert natural language to SQL query."""
        messages = [
            {
                "role": "system",
                "content": f"""You are a SQL expert assistant. Convert natural language questions into PostgreSQL queries.

{self.SCHEMA_CONTEXT}

Rules:
1. ONLY generate SELECT queries - no INSERT, UPDATE, DELETE, DROP, or any data modification
2. Always use table aliases for clarity
3. Include relevant JOINs when needed
4. Use appropriate aggregations (COUNT, SUM, AVG) for summary questions
5. Format currency values and percentages appropriately
6. Limit results to 100 rows maximum
7. Return ONLY the SQL query, nothing else

If the question cannot be answered with the available schema, return: SELECT 'Cannot answer this question' as message"""
            }
        ]
        
        # Add recent conversation history for context
        for msg in history[-4:]:
            messages.append(msg)
        
        messages.append({
            "role": "user",
            "content": f"Convert this to SQL: {message}"
        })
        
        sql = openai_service.chat_completion(messages, temperature=0.1, max_tokens=500)
        
        # Clean the response
        sql = sql.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
    
    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL query for security - only allow SELECT statements."""
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Forbidden keywords
        forbidden = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
            'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE',
            '--', ';--', '/*', '*/', 'UNION SELECT'
        ]
        
        for word in forbidden:
            if word in sql_upper:
                return False
        
        # Check that only allowed tables are referenced
        sql_lower = sql.lower()
        for table in self.ALLOWED_TABLES:
            sql_lower = sql_lower.replace(table, '')
        
        # Check for suspicious patterns
        if re.search(r'\b(pg_|information_schema|sys\.)\b', sql_lower, re.IGNORECASE):
            return False
        
        return True
    
    def _execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query safely and return results."""
        result = self.db.execute(text(sql))
        columns = result.keys()
        rows = result.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def _generate_response(
        self,
        question: str,
        sql: str,
        data: List[Dict[str, Any]]
    ) -> str:
        """Generate a natural language response from query results."""
        if not data:
            return "I couldn't find any data matching your query."
        
        # Summarize data for the LLM
        data_summary = str(data[:20])  # First 20 rows for context
        total_rows = len(data)
        
        messages = [
            {
                "role": "system",
                "content": """You are a helpful sales analytics assistant. Provide clear, concise insights 
based on the data. Format numbers nicely (use commas for thousands, currency symbols where appropriate).
Keep responses focused and actionable. If showing multiple records, summarize the key findings."""
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Query returned {total_rows} rows. Sample data:
{data_summary}

Provide a helpful response summarizing the data and any insights."""
            }
        ]
        
        return openai_service.chat_completion(messages, temperature=0.5, max_tokens=800)

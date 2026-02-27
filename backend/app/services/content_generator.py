from typing import List, Optional
from app.services.openai_client import openai_service
from app.schemas.ai import ContentGenerateRequest, ContentGenerateResponse


class ContentGeneratorService:
    """AI-powered marketing content generation."""
    
    PLATFORM_GUIDELINES = {
        "linkedin": {
            "max_length": 3000,
            "style": "Professional, thought-leadership focused. Use line breaks for readability.",
            "tips": "Start with a hook, use emojis sparingly, end with a call-to-action or question."
        },
        "email": {
            "max_length": 500,
            "style": "Personalized, direct, value-focused. Clear subject line.",
            "tips": "Keep subject under 50 chars, personalize greeting, single clear CTA."
        },
        "twitter": {
            "max_length": 280,
            "style": "Punchy, engaging, hashtag-optimized.",
            "tips": "Use 1-2 relevant hashtags, create urgency, be conversational."
        },
        "blog": {
            "max_length": 2000,
            "style": "Informative, SEO-friendly, structured with headers.",
            "tips": "Include intro hook, use subheadings, end with clear takeaways."
        },
        "facebook": {
            "max_length": 500,
            "style": "Engaging, community-focused, shareable.",
            "tips": "Ask questions, use visuals references, encourage engagement."
        }
    }
    
    def generate_content(self, request: ContentGenerateRequest) -> ContentGenerateResponse:
        """Generate marketing content variations."""
        platform = request.platform.lower()
        guidelines = self.PLATFORM_GUIDELINES.get(platform, self.PLATFORM_GUIDELINES["linkedin"])
        
        max_length = request.max_length or guidelines["max_length"]
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert marketing copywriter specializing in B2B content. 
Generate compelling marketing copy that converts.

Platform: {platform.upper()}
Guidelines: {guidelines['style']}
Tips: {guidelines['tips']}
Maximum length: {max_length} characters per variation

Your copy should:
- Speak directly to the target audience's pain points
- Highlight clear value propositions
- Include appropriate calls-to-action
- Match the specified tone exactly
- Be industry-specific and relevant"""
            },
            {
                "role": "user",
                "content": f"""Create 3 distinct variations of marketing copy with the following parameters:

Target Audience: {request.target_audience}
Industry: {request.industry}
Tone: {request.tone}
Platform: {platform}
{f'Topic/Focus: {request.topic}' if request.topic else ''}
{f'Key Points to Include: {", ".join(request.key_points)}' if request.key_points else ''}

Return a JSON object with:
- variations: array of 3 different copy variations
- platform: the platform name
- tone: the tone used
- tips: array of 2-3 tips for using this content effectively"""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.8)
        
        return ContentGenerateResponse(
            variations=result.get('variations', []),
            platform=platform,
            tone=request.tone,
            metadata={
                "target_audience": request.target_audience,
                "industry": request.industry,
                "tips": result.get('tips', []),
                "max_length": max_length
            }
        )
    
    def generate_email_sequence(
        self,
        target_audience: str,
        industry: str,
        campaign_goal: str,
        num_emails: int = 3
    ) -> List[dict]:
        """Generate a sequence of marketing emails."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert email marketing specialist. Create compelling email sequences 
that nurture leads through the sales funnel. Each email should build on the previous one."""
            },
            {
                "role": "user",
                "content": f"""Create a {num_emails}-email nurture sequence:

Target Audience: {target_audience}
Industry: {industry}
Campaign Goal: {campaign_goal}

For each email, provide:
- subject_line: Compelling subject (under 50 chars)
- preview_text: Email preview text (under 100 chars)
- body: Email body content
- cta_text: Call-to-action button text
- send_delay_days: Days to wait after previous email (0 for first email)

Return as JSON with key 'emails' containing array of email objects."""
            }
        ]
        
        result = openai_service.chat_completion_json(messages, temperature=0.7)
        return result.get('emails', [])
    
    def optimize_content(
        self,
        original_content: str,
        platform: str,
        optimization_goal: str
    ) -> dict:
        """Optimize existing content for better performance."""
        messages = [
            {
                "role": "system",
                "content": """You are a content optimization expert. Analyze and improve marketing content 
for better engagement and conversion."""
            },
            {
                "role": "user",
                "content": f"""Optimize this {platform} content for: {optimization_goal}

Original content:
{original_content}

Provide:
- optimized_content: Improved version
- changes_made: List of changes and why
- predicted_improvement: Expected improvement areas
- a_b_test_suggestion: Variation to test against"""
            }
        ]
        
        return openai_service.chat_completion_json(messages, temperature=0.6)

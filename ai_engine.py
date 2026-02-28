import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_campaign(insights):
    prompt = f"""
    Based on:
    Total Sales: {insights['total_sales']}
    Avg Sales: {insights['avg_sales']}
    Top Product: {insights['top_product']}
    
    Generate a marketing campaign strategy.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
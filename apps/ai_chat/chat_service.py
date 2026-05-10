import os
from groq import Groq
from .guardrail import is_stock_related

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

SYSTEM_PROMPT = """You are StockAI Pro Assistant, an expert stock market analyst for Indian markets (NSE/BSE).

You ONLY answer questions related to:
- Stock markets (NSE, BSE, Sensex, Nifty)
- Individual stocks and companies
- Trading strategies and techniques
- Investment advice and portfolio management
- Financial metrics (PE ratio, EPS, RSI, etc.)
- Market news and analysis
- Mutual funds and ETFs
- Indian economy and RBI policies

Keep responses concise, clear and actionable.
Always mention risks when giving investment advice.
Format numbers in Indian style (Lakhs, Crores).
"""

def get_ai_response(user_message):
    if not is_stock_related(user_message):
        return {
            'response': "I am designed to answer only stock market related queries. Please ask me about stocks, trading, investments, or financial markets!",
            'is_blocked': True
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return {
            'response': response.choices[0].message.content,
            'is_blocked': False
        }
    except Exception as e:
        return {
            'response': f"Error: {str(e)}",
            'is_blocked': False
        }
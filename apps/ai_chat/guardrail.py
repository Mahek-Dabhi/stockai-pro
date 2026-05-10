STOCK_KEYWORDS = [
    'stock', 'share', 'market', 'trading', 'invest', 'portfolio',
    'nse', 'bse', 'sensex', 'nifty', 'equity', 'dividend', 'ipo',
    'bull', 'bear', 'price', 'buy', 'sell', 'profit', 'loss',
    'reliance', 'tcs', 'infosys', 'hdfc', 'wipro', 'infy',
    'pe ratio', 'eps', 'revenue', 'earnings', 'fundamental',
    'technical', 'rsi', 'moving average', 'chart', 'trend',
    'broker', 'demat', 'sebi', 'mutual fund', 'etf', 'index',
    'rupee', 'currency', 'finance', 'financial', 'economy',
    'gdp', 'inflation', 'interest rate', 'rbi', 'monetary',
    'sector', 'cap', 'valuation', 'return', 'yield', 'bond',
    'today', 'gain', 'down', 'up', 'fall', 'rise', 'crash',
    'rally', 'correction', 'volatile', 'volatility', 'week',
    'month', 'annual', 'quarter', 'q1', 'q2', 'q3', 'q4',
    'tatamotors', 'tata', 'bajaj', 'adani', 'sbi', 'lic',
    'zerodha', 'groww', 'upstox', 'angel', 'smallcap',
    'midcap', 'largecap', 'bluechip', 'penny', 'futures',
    'options', 'derivative', 'hedge', 'long', 'short',
]

GREETINGS = [
    'hi', 'hello', 'hey', 'hii', 'helo', 'good morning',
    'good evening', 'good afternoon', 'how are you', 'thanks',
    'thank you', 'ok', 'okay', 'bye', 'help'
]

def is_stock_related(question):
    question_lower = question.lower().strip()
    if any(question_lower == g or question_lower.startswith(g) for g in GREETINGS):
        return True
    return any(keyword in question_lower for keyword in STOCK_KEYWORDS)
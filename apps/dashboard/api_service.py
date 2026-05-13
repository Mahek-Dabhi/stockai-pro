import yfinance as yf
import requests
from datetime import datetime
import pytz

# ── Browser session — bypasses Yahoo Finance cloud IP blocking ────────────────
# Yahoo Finance blocks AWS/Render server IPs but allows browser-like requests.
# Passing this session to yf.Ticker() makes requests look like a real browser.
SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection':      'keep-alive',
})

# ── Market hours ──────────────────────────────────────────────────────────────

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    open_time  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    is_weekday = now.weekday() < 5
    return is_weekday and open_time <= now <= close_time


# ── Default watchlist ─────────────────────────────────────────────────────────

DEFAULT_STOCKS = [
    'RELIANCE',
    'TCS',
    'HDFCBANK',
    'INFY',
    'ICICIBANK',
    'WIPRO',
]


# ── Single stock fetch ────────────────────────────────────────────────────────

def get_stock_data(symbol):
    """
    Fetch live + historical data for one NSE stock.
    Uses browser-like session to bypass Yahoo Finance IP blocks on Render.
    Returns a dict on success, None on any failure.
    """
    suffixes = ['.NS', '.BO']
    ticker = None
    info   = {}

    for suffix in suffixes:
        try:
            # Pass SESSION so yfinance uses browser-like headers
            t = yf.Ticker(symbol + suffix, session=SESSION)
            i = t.info
            price = i.get('currentPrice') or i.get('regularMarketPrice')
            if price:
                ticker = t
                info   = i
                break
        except Exception:
            continue

    if not ticker:
        print(f"[api_service] No price data for {symbol} — skipping.")
        return None

    try:
        current_price = (
            info.get('currentPrice') or
            info.get('regularMarketPrice') or
            info.get('previousClose')
        )
        if not current_price:
            return None

        prev_close = info.get('previousClose') or current_price
        change     = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        hist = ticker.history(period='1mo', auto_adjust=False)
        if hist.empty:
            print(f"[api_service] Empty history for {symbol} — skipping.")
            return None

        chart_dates  = hist.index.strftime('%d %b').tolist()
        chart_prices = [round(float(p), 2) for p in hist['Close'].tolist()]

        ohlc_data = []
        for idx, row in hist.iterrows():
            c = float(row['Close'])
            if c < 1:
                continue
            ohlc_data.append({
                'x': int(idx.timestamp() * 1000),
                'o': round(float(row['Open']),  2),
                'h': round(float(row['High']),  2),
                'l': round(float(row['Low']),   2),
                'c': round(c, 2),
            })

        return {
            'symbol':       symbol,
            'name':         info.get('longName') or info.get('shortName') or symbol,
            'price':        round(current_price, 2),
            'change':       round(change, 2),
            'change_pct':   round(change_pct, 2),
            'volume':       info.get('volume') or 0,
            'market_cap':   info.get('marketCap') or 0,
            'high':         round(info.get('dayHigh')  or current_price, 2),
            'low':          round(info.get('dayLow')   or current_price, 2),
            'chart_dates':  chart_dates,
            'chart_prices': chart_prices,
            'ohlc_data':    ohlc_data,
            'is_positive':  change >= 0,
        }

    except Exception as e:
        print(f"[api_service] Error fetching {symbol}: {e}")
        return None


# ── Multiple stocks ───────────────────────────────────────────────────────────

def get_multiple_stocks(symbols):
    stocks = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        if data:
            stocks.append(data)
    return stocks
import os
import requests
import time
from datetime import datetime
import pytz

# ── Alpha Vantage API ─────────────────────────────────────────────────────────
# Free tier: 25 requests/day, works on all cloud servers, supports BSE/NSE
ALPHA_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
BASE_URL   = 'https://www.alphavantage.co/query'

# ── 5-minute in-memory cache ──────────────────────────────────────────────────
# Each stock cached for 5 minutes — stays well within 25 req/day free limit
_cache   = {}
CACHE_TTL = 300  # seconds

def _cache_get(key):
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None

def _cache_set(key, data):
    _cache[key] = (data, time.time())


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

# Company display names (Alpha Vantage daily endpoint has no name field)
NAME_MAP = {
    'RELIANCE':  'Reliance Industries Limited',
    'TCS':       'Tata Consultancy Services',
    'HDFCBANK':  'HDFC Bank Limited',
    'INFY':      'Infosys Limited',
    'ICICIBANK': 'ICICI Bank Limited',
    'WIPRO':     'Wipro Limited',
}


# ── Single stock fetch ────────────────────────────────────────────────────────

def get_stock_data(symbol):
    """
    Fetch live + 30-day historical data via Alpha Vantage.
    Caches each stock for 5 minutes to stay within free tier limits.
    """
    # Return cached data if fresh
    cached = _cache_get(symbol)
    if cached:
        return cached

    # Alpha Vantage Indian stock format: SYMBOL.BSE
    av_symbol = f"{symbol}.BSE"

    try:
        r = requests.get(BASE_URL, params={
            'function':   'TIME_SERIES_DAILY',
            'symbol':     av_symbol,
            'outputsize': 'compact',
            'apikey':     ALPHA_KEY,
        }, timeout=15)

        data = r.json()

        if 'Error Message' in data:
            print(f"[api_service] Symbol not found: {symbol}")
            return None
        if 'Note' in data or 'Information' in data:
            msg = data.get('Note') or data.get('Information', '')
            print(f"[api_service] Rate limit for {symbol}: {msg[:60]}")
            return None

        time_series = data.get('Time Series (Daily)', {})
        if not time_series:
            print(f"[api_service] No data for {symbol}")
            return None

        # Sort oldest → newest
        sorted_dates = sorted(time_series.keys())
        recent_dates = sorted_dates[-30:]
        latest_date  = sorted_dates[-1]
        latest       = time_series[latest_date]

        current_price = round(float(latest['4. close']), 2)
        high          = round(float(latest['2. high']),  2)
        low           = round(float(latest['3. low']),   2)
        volume        = int(float(latest['5. volume']))

        prev_close = round(float(
            time_series[sorted_dates[-2]]['4. close']
        ), 2) if len(sorted_dates) >= 2 else current_price

        change     = round(current_price - prev_close, 2)
        change_pct = round((change / prev_close * 100) if prev_close else 0.0, 2)

        chart_dates  = []
        chart_prices = []
        ohlc_data    = []

        for date_str in recent_dates:
            bar = time_series[date_str]
            try:
                dt    = datetime.strptime(date_str, '%Y-%m-%d')
                close = round(float(bar['4. close']), 2)
                open_ = round(float(bar['1. open']),  2)
                h     = round(float(bar['2. high']),  2)
                l     = round(float(bar['3. low']),   2)
                chart_dates.append(dt.strftime('%d %b'))
                chart_prices.append(close)
                ohlc_data.append({
                    'x': int(dt.timestamp() * 1000),
                    'o': open_, 'h': h, 'l': l, 'c': close,
                })
            except Exception:
                continue

        if not chart_prices:
            return None

        result = {
            'symbol':       symbol,
            'name':         NAME_MAP.get(symbol, symbol),
            'price':        current_price,
            'change':       change,
            'change_pct':   change_pct,
            'volume':       volume,
            'market_cap':   0,
            'high':         high,
            'low':          low,
            'chart_dates':  chart_dates,
            'chart_prices': chart_prices,
            'ohlc_data':    ohlc_data,
            'is_positive':  change >= 0,
        }

        _cache_set(symbol, result)
        return result

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
import requests
import os

def fetch_stock_news(symbol, company_name):
    api_key = os.getenv('NEWS_API_KEY')
    query = f"{company_name} OR {symbol} stock India"
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('status') == 'ok':
            articles = []
            for article in data.get('articles', []):
                if article.get('title') and article.get('description'):
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_at': article['publishedAt'][:10],
                    })
            return articles
    except Exception as e:
        return []
    return []
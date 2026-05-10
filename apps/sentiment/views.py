from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.dashboard.api_service import get_stock_data, DEFAULT_STOCKS
from .news_fetcher import fetch_stock_news
from .analyzer import analyze_news_sentiment

@login_required
def sentiment_view(request):
    symbol = request.GET.get('symbol', 'RELIANCE')
    stock = get_stock_data(symbol)
    articles = []
    overall = None

    if stock:
        raw_articles = fetch_stock_news(symbol, stock['name'])
        if raw_articles:
            articles, overall = analyze_news_sentiment(raw_articles)

    return render(request, 'sentiment/sentiment.html', {
        'stock': stock,
        'symbol': symbol,
        'articles': articles,
        'overall': overall,
        'stocks_list': DEFAULT_STOCKS,
    })
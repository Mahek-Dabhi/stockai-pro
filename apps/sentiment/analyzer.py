from textblob import TextBlob

def analyze_sentiment(text):
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            sentiment = 'Positive'
            color = 'teal'
            icon = 'fa-arrow-trend-up'
        elif polarity < -0.1:
            sentiment = 'Negative'
            color = 'crimson'
            icon = 'fa-arrow-trend-down'
        else:
            sentiment = 'Neutral'
            color = 'amber'
            icon = 'fa-minus'
        return {
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'color': color,
            'icon': icon,
        }
    except:
        return {
            'sentiment': 'Neutral',
            'polarity': 0,
            'color': 'amber',
            'icon': 'fa-minus',
        }

def analyze_news_sentiment(articles):
    if not articles:
        return []
    results = []
    total_polarity = 0
    for article in articles:
        text = f"{article['title']} {article['description']}"
        sentiment = analyze_sentiment(text)
        results.append({**article, **sentiment})
        total_polarity += sentiment['polarity']
    avg_polarity = total_polarity / len(articles)
    overall = analyze_sentiment_from_polarity(avg_polarity)
    return results, overall

def analyze_sentiment_from_polarity(polarity):
    if polarity > 0.1:
        return {'sentiment': 'Positive', 'polarity': round(polarity, 3), 'color': 'teal', 'score': round((polarity + 1) * 50, 1)}
    elif polarity < -0.1:
        return {'sentiment': 'Negative', 'polarity': round(polarity, 3), 'color': 'crimson', 'score': round((polarity + 1) * 50, 1)}
    else:
        return {'sentiment': 'Neutral', 'polarity': round(polarity, 3), 'color': 'amber', 'score': 50.0}
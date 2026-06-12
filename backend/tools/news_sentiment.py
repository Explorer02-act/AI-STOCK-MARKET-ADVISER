from __future__ import annotations

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from backend.cache import cache
from backend.monitoring import UsageEvent, usage_monitor
from configs.settings import NEWS_API_KEY

analyzer = SentimentIntensityAnalyzer()


def get_news_sentiment(ticker: str) -> dict:
    ticker = ticker.strip().upper()
    cache_key = f"news:sentiment:{ticker}"
    cached = cache.get_json(cache_key)
    if cached:
        usage_monitor.record(UsageEvent("redis", "news_sentiment_cache", "hit"))
        return cached

    if not NEWS_API_KEY:
        return {
            "ticker": ticker,
            "sentiment": "neutral",
            "score": 0,
            "articles": [],
            "error": "NEWS_API_KEY is not configured.",
        }

    company = ticker.replace(".NS", "")
    try:
        usage_monitor.record(UsageEvent("newsapi", "everything", "request"))
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": f"{company} stock",
                "language": "en",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            },
            timeout=10,
        )
        remaining = response.headers.get("X-RateLimit-Remaining")
        response.raise_for_status()
        articles = response.json().get("articles", [])

        if not articles:
            data = {"ticker": ticker, "sentiment": "neutral", "score": 0, "articles": []}
            cache.set_json(cache_key, data, ttl_seconds=900)
            return data

        scores = []
        headlines = []
        for article in articles:
            title = article.get("title", "")
            score = analyzer.polarity_scores(title)["compound"]
            scores.append(score)
            headlines.append({"title": title, "score": round(score, 3)})

        avg_score = sum(scores) / len(scores)
        sentiment = "positive" if avg_score > 0.05 else "negative" if avg_score < -0.05 else "neutral"

        data = {
            "ticker": ticker,
            "sentiment": sentiment,
            "score": round(avg_score, 3),
            "articles": headlines,
        }
        usage_monitor.record(
            UsageEvent(
                "newsapi",
                "everything",
                "success",
                rate_limit_remaining=int(remaining) if remaining and remaining.isdigit() else None,
            )
        )
        cache.set_json(cache_key, data, ttl_seconds=900)
        return data
    except requests.RequestException as e:
        usage_monitor.record_failure("newsapi", "everything", e)
        return {
            "ticker": ticker,
            "sentiment": "neutral",
            "score": 0,
            "articles": [],
            "error": "News API request failed. Check network access and NEWS_API_KEY.",
        }
    except Exception as e:
        usage_monitor.record_failure("newsapi", "everything", e)
        return {"ticker": ticker, "sentiment": "neutral", "score": 0, "error": str(e)}

"""
News signal collector.
Monitors company mentions in news sources for expansion, product launch,
and leadership change signals. Uses SerpAPI Google News endpoint.
"""
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.models import Company, Signal, SignalType, SignalSource

logger = get_logger(__name__)

SERPAPI_BASE = "https://serpapi.com/search"

# Keywords that indicate specific signal types in news headlines
SIGNAL_KEYWORD_MAP = {
    SignalType.EXPANSION: [
        "expands to", "launches in", "opens office", "new market",
        "international expansion", "new region", "series", "raises",
    ],
    SignalType.LEADERSHIP_CHANGE: [
        "appoints", "names", "hires", "joins as", "new ceo", "new cto",
        "new cpo", "new vp", "new head of", "promoted to",
    ],
    SignalType.PRODUCT_LAUNCH: [
        "launches", "announces", "introduces", "unveils", "releases",
        "new product", "new feature", "general availability",
    ],
    SignalType.FUNDING: [
        "raises", "funding", "series a", "series b", "series c",
        "million", "venture", "investment",
    ],
}


def _detect_signal_type(headline: str) -> SignalType | None:
    """Map a news headline to a signal type based on keywords."""
    headline_lower = headline.lower()
    for signal_type, keywords in SIGNAL_KEYWORD_MAP.items():
        if any(kw in headline_lower for kw in keywords):
            return signal_type
    return SignalType.NEWS  # generic fallback


def _signal_strength_for_news(signal_type: SignalType) -> float:
    """News-sourced signals are weaker than direct API signals."""
    strengths = {
        SignalType.FUNDING: 0.20,
        SignalType.LEADERSHIP_CHANGE: 0.15,
        SignalType.EXPANSION: 0.10,
        SignalType.PRODUCT_LAUNCH: 0.08,
        SignalType.NEWS: 0.05,
    }
    return strengths.get(signal_type, 0.05)


def fetch_company_news(company_name: str, domain: str | None = None) -> list[dict]:
    """
    Fetch recent news articles for a company via SerpAPI Google News.
    Returns list of article dicts.
    """
    if not settings.SERPAPI_KEY:
        return []  # graceful degradation

    query = f'"{company_name}"'
    if domain:
        query += f" OR site:{domain}"

    try:
        resp = httpx.get(
            SERPAPI_BASE,
            params={
                "engine": "google_news",
                "q": query,
                "api_key": settings.SERPAPI_KEY,
                "num": 10,
                "tbs": "qdr:m",  # past month
            },
            timeout=20.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("news_results", [])
    except httpx.HTTPStatusError as e:
        logger.warning(
            "serpapi_request_failed",
            company=company_name,
            status=e.response.status_code,
        )
        return []
    except Exception as e:
        logger.warning("serpapi_error", company=company_name, error=str(e))
        return []


def run_news_collection(db: Session, workspace_id: str) -> dict:
    """
    Collect news signals for all active companies in a workspace.
    Runs after Apollo collection — companies must already exist.
    """
    companies = (
        db.query(Company)
        .filter_by(workspace_id=workspace_id)
        .limit(100)  # cap per run to manage API costs
        .all()
    )

    stats = {"companies_processed": 0, "signals_created": 0, "errors": 0}
    now = datetime.now(timezone.utc)

    for company in companies:
        try:
            articles = fetch_company_news(company.name, company.domain)
            for article in articles[:5]:  # max 5 signals per company per run
                headline = article.get("title", "")
                if not headline:
                    continue

                signal_type = _detect_signal_type(headline)
                strength = _signal_strength_for_news(signal_type)

                # Parse article date
                try:
                    from dateutil.parser import parse
                    article_date = parse(article.get("date", "")).replace(tzinfo=timezone.utc)
                except Exception:
                    article_date = now

                signal = Signal(
                    workspace_id=workspace_id,
                    company_id=company.id,
                    signal_type=signal_type,
                    signal_source=SignalSource.NEWS,
                    title=headline[:500],
                    description=article.get("snippet", "")[:1000],
                    url=article.get("link"),
                    base_strength=strength,
                    decayed_strength=strength,
                    detected_at=article_date,
                    signal_metadata={
                        "source": article.get("source", {}).get("name"),
                        "published_date": article.get("date"),
                    },
                )
                db.add(signal)
                stats["signals_created"] += 1

            stats["companies_processed"] += 1

        except Exception as e:
            logger.error(
                "news_collection_company_error",
                company=company.name,
                error=str(e),
            )
            stats["errors"] += 1

    db.commit()
    logger.info("news_collection_complete", workspace_id=workspace_id, **stats)
    return stats

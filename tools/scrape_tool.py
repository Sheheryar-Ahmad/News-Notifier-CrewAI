import re

import requests
from crewai.tools import tool

ERROR_WORDS = ["CAPTCHA", "robot", "unusual activity", "rate limit", "404", "Not Found"]
MAX_ARTICLE_CHARS = 5000

_scrape_cache = {"result": None}


def reset_scrape_state():
    _scrape_cache["result"] = None


def _extract_urls(text: str) -> list[str]:
    if not text:
        return []

    urls = re.findall(r"https?://[^\s,\]\"'<>]+", str(text))
    cleaned = []
    seen = set()
    for url in urls:
        url = url.rstrip(".,)")
        if url not in seen:
            seen.add(url)
            cleaned.append(url)
    return cleaned


def _scrape_url(link: str) -> str:
    jina_url = f"https://r.jina.ai/{link}"
    response = requests.get(jina_url, timeout=30)
    text = response.text

    for word in ERROR_WORDS:
        if word in text:
            return "Error: Article is blocked by CAPTCHA or paywall."

    return text[:MAX_ARTICLE_CHARS]


@tool
def scrape_first_article(urls_or_text: str) -> str:
    """Scrape exactly one article. Pass the search results text or URL list.
    Tries the first URL, then the second only if the first fails. Call once."""
    if _scrape_cache["result"] is not None:
        return _scrape_cache["result"]

    urls = _extract_urls(urls_or_text)
    if not urls:
        return "Error: No valid URLs found in the input."

    for url in urls[:2]:
        result = _scrape_url(url)
        if not result.startswith("Error"):
            _scrape_cache["result"] = result
            return result

    return "Error: Could not scrape any article from the provided URLs."


@tool
def scrape_tool(link: str) -> str:
    """Scrape a single article URL. Prefer scrape_first_article for the crew pipeline."""
    if _scrape_cache["result"] is not None:
        return _scrape_cache["result"]

    result = _scrape_url(link)
    if not result.startswith("Error"):
        _scrape_cache["result"] = result
    return result

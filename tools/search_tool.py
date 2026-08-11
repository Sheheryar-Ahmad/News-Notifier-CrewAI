from crewai.tools import tool
import requests
from dotenv import load_dotenv
import os

load_dotenv()

X_API_KEY = os.getenv("X_API_KEY")

_search_cache = {"result": None}


def reset_search_state():
    _search_cache["result"] = None


@tool
def search_tool(query: str):
    """Search the web once for the latest trending news articles on a topic."""
    if _search_cache["result"] is not None:
        return _search_cache["result"]

    url = "https://google.serper.dev/news"

    payload = {"q": query}

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": X_API_KEY,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    data = response.json()
    news_items = data.get("news", [])

    articles = []
    for item in news_items:
        articles.append({
            "title": item.get("title"),
            "link": item.get("link"),
        })

    result = articles[:3]
    _search_cache["result"] = result
    return result

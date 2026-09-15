from ddgs import DDGS
from langchain.tools import tool
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import requests
import re


def clean_text(text: str) -> str:
    """Collapse excess whitespace and drop empty/junk lines"""

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    text = "\n".join(lines)
    return re.sub(r"[ \t]+", " ", text).strip()

@tool
def web_search(topic:str) -> str:
    """Search the web for a given topics"""

    output = []
    results = DDGS().text(topic, max_results=5)
    for r in results:
        output.append(
            f"Title: {r['title']}\nContent: {r['body'][:300]}\nURL: {r['href']}"
        )
    return "\n\n".join(output)

@tool
def web_scrape_url(url:str) -> str:
    """Scrape a given URL and return its main readable text content"""

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"

    text = trafilatura.extract(response.text)
    if text:
        return clean_text(text)

    doc = Document(response.text)
    soup = BeautifulSoup(doc.summary(), "html.parser")
    text = soup.get_text(separator="\n", strip=True)

    return clean_text(text) if text else "No content could be extracted from the URL."


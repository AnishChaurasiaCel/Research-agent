from src.tools.tools import web_search, web_scrape_url
from rich import print

result = web_scrape_url.invoke('https://www.geeksforgeeks.org/artificial-intelligence/agentic-ai/')
print(result)
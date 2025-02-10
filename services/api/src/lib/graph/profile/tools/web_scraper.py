import requests
from bs4 import BeautifulSoup

def web_scraper(url: str) -> str:
    """Scrape website content using BeautifulSoup"""
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text().replace("\n\n\n", " ")
    except Exception as e:
        raise e

        

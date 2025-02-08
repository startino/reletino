import requests
from bs4 import BeautifulSoup

def web_scraper(url: str) -> str:
    """Scrape website content using BeautifulSoup"""
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text().replace("\n\n\n", " ")

if __name__ == "__main__":
    print(web_scraper("https://starti.no/"))
        

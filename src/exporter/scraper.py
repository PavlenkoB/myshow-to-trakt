# src/exporter/scraper.py
import time
import re
from bs4 import BeautifulSoup

class IMDbScraper:
    def __init__(self, session):
        self.session = session

    def get_imdb_id(self, show_id):
        url = f"https://myshows.me/view/{show_id}/"
        try:
            time.sleep(1.5)  # Rate limiting
            resp = self.session.get(url)
            if resp.status_code != 200:
                return None
            
            soup = BeautifulSoup(resp.text, 'lxml')
            # Look for IMDb link
            imdb_link = soup.find('a', href=lambda href: href and 'imdb.com/title/' in href)
            if imdb_link:
                # Extract ttXXXXXXX via regex
                match = re.search(r'tt(\d+)', imdb_link['href'])
                if match:
                    num_part = match.group(1)
                    return f"tt{num_part.zfill(7)}"
        except Exception:
            pass
        return None

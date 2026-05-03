import os
from dotenv import load_dotenv
from src.exporter.session import SessionManager
from src.exporter.scraper import IMDbScraper
from src.exporter.cache import IMDbCache
from src.exporter.processor import DataProcessor

# Load environment variables
load_dotenv()

# === SETTINGS ===
USERNAME = os.getenv('MYSHOWS_USERNAME')
PASSWORD = os.getenv('MYSHOWS_PASSWORD')
SESSION_COOKIE = os.getenv('MYSHOWS_COOKIE')
CSV_FILENAME = 'tmp/myshows_export.csv'
CACHE_FILENAME = 'tmp/imdb_cache.json'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ================

def main():
    # 1. Initialize session
    manager = SessionManager(USER_AGENT)
    if not manager.login(USERNAME, PASSWORD, SESSION_COOKIE):
        return
    
    # 2. Initialize components
    session = manager.get_session()
    cache = IMDbCache(CACHE_FILENAME)
    scraper = IMDbScraper(session)
    processor = DataProcessor(session, scraper, cache)

    # 3. Process export
    processor.process_all(CSV_FILENAME)

if __name__ == "__main__":
    main()

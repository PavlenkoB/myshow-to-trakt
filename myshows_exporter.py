import os
from dotenv import load_dotenv
from src.exporter.session import SessionManager
from src.exporter.scraper import IMDbScraper
from src.exporter.cache import IMDbCache, StateCache
from src.exporter.processor import DataProcessor

# Load environment variables
load_dotenv()

# === SETTINGS ===
USERNAME = os.getenv('MYSHOWS_USERNAME')
PASSWORD = os.getenv('MYSHOWS_PASSWORD')
SESSION_COOKIE = os.getenv('MYSHOWS_COOKIE')
EXPORT_LIMIT = os.getenv('EXPORT_LIMIT')
CSV_FILENAME = 'tmp/myshows_export.csv'
CACHE_FILENAME = 'tmp/imdb_cache.json'
STATE_CACHE_FILENAME = 'tmp/tvshow_state_cache.json'
EPISODE_CACHE_FILENAME = 'tmp/tvshow_episode_cache.json'
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
    state_cache = StateCache(STATE_CACHE_FILENAME)
    episode_cache = StateCache(EPISODE_CACHE_FILENAME)
    scraper = IMDbScraper(session)
    processor = DataProcessor(session, scraper, cache, state_cache, episode_cache)

    # 3. Process export
    limit = int(EXPORT_LIMIT) if EXPORT_LIMIT and EXPORT_LIMIT.isdigit() else None
    processor.process_all(CSV_FILENAME, limit=limit)

if __name__ == "__main__":
    main()

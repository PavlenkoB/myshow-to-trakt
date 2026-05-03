import requests
import hashlib
import csv
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm import tqdm

# Load environment variables
load_dotenv()

# === SETTINGS ===
USERNAME = os.getenv('MYSHOWS_USERNAME')
PASSWORD = os.getenv('MYSHOWS_PASSWORD')
SESSION_COOKIE = os.getenv('MYSHOWS_COOKIE') # Optional: 'PHPSESSID=...'
CSV_FILENAME = 'myshows_export.csv'
CACHE_FILENAME = 'imdb_cache.json'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ================

class IMDbCache:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def get(self, show_id):
        return self.data.get(str(show_id))

    def set(self, show_id, imdb_id):
        self.data[str(show_id)] = imdb_id
        self.save()

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def login(self):
        if SESSION_COOKIE:
            print("[+] Using provided session cookie.")
            # Expected format: PHPSESSID=xxx; other=yyy
            for cookie in SESSION_COOKIE.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    self.session.cookies.set(name, value, domain='myshows.me')
            return True

        if not USERNAME or not PASSWORD:
            print("[-] Error: Missing credentials in .env")
            return False

        print(f"[*] Logging in as: {USERNAME}")
        md5_password = hashlib.md5(PASSWORD.encode('utf-8')).hexdigest()
        login_url = f"https://api.myshows.me/profile/login?login={USERNAME}&password={md5_password}"
        resp = self.session.get(login_url)
        
        if resp.status_code == 200:
            print("[+] Successful authorization.")
            return True
        print(f"[-] Auth failed: {resp.status_code}")
        return False

class IMDbScraper:
    def __init__(self, session):
        self.session = session

    def get_imdb_id(self, show_id):
        url = f"https://myshows.me/view/{show_id}/"
        try:
            time.sleep(1.5) # Rate limiting
            resp = self.session.get(url)
            if resp.status_code != 200:
                return None
            
            soup = BeautifulSoup(resp.text, 'lxml')
            # Look for IMDb link
            imdb_link = soup.find('a', href=lambda href: href and 'imdb.com/title/' in href)
            if imdb_link:
                # Extract ttXXXXXXX
                parts = imdb_link['href'].split('/')
                for p in parts:
                    if p.startswith('tt'):
                        return p
        except Exception:
            pass
        return None

def main():
    manager = SessionManager()
    if not manager.login():
        return

    cache = IMDbCache(CACHE_FILENAME)
    scraper = IMDbScraper(manager.session)

    # 1. Fetch show list
    print("[*] Downloading shows list...")
    shows_resp = manager.session.get("https://api.myshows.me/profile/shows/")
    if shows_resp.status_code != 200:
        print("[-] Failed to fetch shows list.")
        return
    shows_data = shows_resp.json()

    export_data = []
    print("[*] Processing shows and scraping IMDb IDs...")
    
    # Sort show IDs to ensure consistent progress
    show_ids = sorted(shows_data.keys())
    
    for show_id in tqdm(show_ids, desc="Shows"):
        info = shows_data[show_id]
        title = info.get('title')
        
        # Get IMDb ID (from cache or scraper)
        imdb_id = cache.get(show_id)
        if not imdb_id:
            imdb_id = scraper.get_imdb_id(show_id)
            if imdb_id:
                cache.set(show_id, imdb_id)
        
        # Determine if it's "Watch Later" (status 'later')
        # Note: v1 API might return watchStatus or we infer it
        watch_status = info.get('watchStatus')
        
        # Episodes (History)
        if 'episodes' in info and info['episodes']:
            for ep in info['episodes']:
                watched_at = ""
                raw_date = ep.get('watchDate')
                if raw_date:
                    try:
                        dt = datetime.strptime(raw_date, "%d.%m.%Y")
                        watched_at = dt.strftime("%Y-%m-%dT12:00:00.000Z")
                    except ValueError:
                        pass
                
                export_data.append({
                    'imdb_id': imdb_id or '',
                    'title': title,
                    'type': 'episode',
                    'season': ep.get('seasonNumber', 1),
                    'episode': ep.get('episodeNumber', 1),
                    'watched_at': watched_at,
                    'rating': (info.get('rating', 0) * 2) if info.get('rating') else ''
                })
        
        # Watchlist (if status is 'later')
        if watch_status == 'later':
            export_data.append({
                'imdb_id': imdb_id or '',
                'title': title,
                'type': 'show',
                'season': '',
                'episode': '',
                'watched_at': '',
                'rating': ''
            })

    # 2. Write CSV
    print(f"[*] Writing {len(export_data)} items to {CSV_FILENAME}...")
    with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['imdb_id', 'title', 'type', 'season', 'episode', 'watched_at', 'rating']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in export_data:
            writer.writerow(row)

    print(f"[+] Done! Exported to {CSV_FILENAME}")

if __name__ == "__main__":
    main()

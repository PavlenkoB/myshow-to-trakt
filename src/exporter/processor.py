import csv
from datetime import datetime
from tqdm import tqdm

class DataProcessor:
    def __init__(self, session, scraper, cache):
        self.session = session
        self.scraper = scraper
        self.cache = cache

    def fetch_shows(self):
        print("[*] Fetching shows from MyShows...")
        # /profile/shows/all/ often returns a more complete list than /profile/shows/
        resp = self.session.get("https://api.myshows.me/profile/shows/")
        if resp.status_code != 200:
            return None
        data = resp.json()
        
        # Try to supplement with 'all' if possible
        try:
            resp_all = self.session.get("https://api.myshows.me/profile/shows/all/")
            if resp_all.status_code == 200:
                data_all = resp_all.json()
                if isinstance(data_all, dict):
                    data.update(data_all)
        except Exception:
            pass
            
        return data

    def process_all(self, csv_filename):
        shows_data = self.fetch_shows()
        if not shows_data:
            print("[-] Failed to fetch shows list.")
            return

        # Summary of statuses
        stats = {}
        for s in shows_data.values():
            status = s.get('watchStatus', 'unknown')
            stats[status] = stats.get(status, 0) + 1
        print(f"[*] Found shows by status: {stats}")

        # Stage 1: Metadata Enrichment
        print("[*] Stage 1: Metadata Enrichment (IMDb IDs)")
        show_ids = sorted(shows_data.keys())
        
        # Filter shows that need scraping
        needs_scraping = [sid for sid in show_ids if not self.cache.get(sid)]
        if needs_scraping:
            for show_id in tqdm(needs_scraping, desc="Scraping IMDb"):
                imdb_id = self.scraper.get_imdb_id(show_id)
                if imdb_id:
                    self.cache.set(show_id, imdb_id)
        else:
            print("[+] All IMDb IDs are already cached.")

        # Stage 2: Data Transformation & Export
        export_data = []
        total_episodes = 0
        
        # Count total episodes first for accurate progress bar
        for show_id in show_ids:
            info = shows_data[show_id]
            if 'episodes' in info and info['episodes']:
                total_episodes += len(info['episodes'])
            if info.get('watchStatus') == 'later':
                total_episodes += 1

        if total_episodes == 0:
            print("[-] No episodes or watchlist items to export.")
            return

        print(f"[*] Stage 2: Exporting {total_episodes} items to CSV...")
        pbar = tqdm(total=total_episodes, desc="Exporting")

        for show_id in show_ids:
            info = shows_data[show_id]
            title = info.get('title')
            imdb_id = self.cache.get(show_id)
            watch_status = info.get('watchStatus')
            rating = (info.get('rating', 0) * 2) if info.get('rating') else ''

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
                        'rating': rating
                    })
                    pbar.update(1)
            
            # Watchlist (if status is 'later')
            elif watch_status == 'later':
                export_data.append({
                    'imdb_id': imdb_id or '',
                    'title': title,
                    'type': 'show',
                    'season': '',
                    'episode': '',
                    'watched_at': '',
                    'rating': ''
                })
                pbar.update(1)

        pbar.close()

        # Write CSV
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['imdb_id', 'title', 'type', 'season', 'episode', 'watched_at', 'rating']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in export_data:
                writer.writerow(row)

        print(f"[+] Export finished! Saved to {csv_filename}")

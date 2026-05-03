import csv
import time
from datetime import datetime
from tqdm import tqdm

class DataProcessor:
    def __init__(self, session, scraper, cache, state_cache, episode_cache):
        self.session = session
        self.scraper = scraper
        self.cache = cache # IMDb cache
        self.state_cache = state_cache # Show metadata cache
        self.episode_cache = episode_cache # Watched episodes cache

    def fetch_show_list(self):
        print("[*] Fetching library from MyShows...")
        resp = self.session.get("https://api.myshows.me/profile/shows/")
        if resp.status_code != 200:
            return None
        return resp.json()

    def fetch_metadata(self, show_id):
        # No trailing slash for general metadata
        url = f"https://api.myshows.me/shows/{show_id}"
        try:
            time.sleep(0.3)
            resp = self.session.get(url)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def fetch_watched_details(self, show_id):
        # With trailing slash for user-specific watched list
        url = f"https://api.myshows.me/profile/shows/{show_id}/"
        try:
            time.sleep(0.3)
            resp = self.session.get(url)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def process_all(self, csv_filename, limit=None):
        # 1. Load Caches
        shows_data = self.state_cache.load() or {}
        episodes_data = self.episode_cache.load() or {}

        # 2. Sync Show List
        base_list_full = self.fetch_show_list()
        if not base_list_full:
            print("[-] Failed to fetch show list.")
            return

        # Apply limit if set
        if limit and isinstance(limit, int):
            print(f"[*] Applying export limit: {limit} shows.")
            # Sort by ID to have deterministic behavior
            limited_ids = sorted(base_list_full.keys(), key=int)[:limit]
            base_list = {sid: base_list_full[sid] for sid in limited_ids}
        else:
            base_list = base_list_full

        # Stage 1: Show Metadata (Title, IMDb, Episode Map)
        stats = {}
        for s in base_list.values():
            status = s.get('watchStatus', 'unknown')
            stats[status] = stats.get(status, 0) + 1
        print(f"[*] Library summary: {stats}")

        to_fetch_meta = []
        for sid in base_list:
            str_sid = str(sid)
            # Fetch if not in cache OR if ep_map is missing
            if str_sid not in shows_data or 'ep_map' not in shows_data[str_sid]:
                to_fetch_meta.append(sid)

        if to_fetch_meta:
            print(f"[*] Stage 1: Syncing metadata for {len(to_fetch_meta)} shows...")
            for show_id in tqdm(to_fetch_meta, desc="Metadata"):
                meta = self.fetch_metadata(show_id)
                if meta:
                    str_sid = str(show_id)
                    ep_map = {}
                    if 'episodes' in meta and isinstance(meta['episodes'], dict):
                        for eid, ep in meta['episodes'].items():
                            ep_map[str(eid)] = {
                                's': ep.get('seasonNumber'),
                                'e': ep.get('episodeNumber')
                            }
                    
                    # Extract IMDb ID if present
                    imdb_id = meta.get('imdbId')
                    if imdb_id:
                        imdb_str = str(imdb_id)
                        if not imdb_str.startswith('tt'):
                            # Pad to 7 digits (standard IMDb ID length)
                            imdb_id = f"tt{imdb_str.zfill(7)}"
                        else:
                            imdb_id = imdb_str
                    
                    shows_data[str_sid] = {
                        'title': meta.get('title'),
                        'imdb_id': imdb_id,
                        'watchStatus': base_list[str_sid].get('watchStatus'),
                        'rating': base_list[str_sid].get('rating'),
                        'ep_map': ep_map
                    }
                    
                    if len(shows_data) % 10 == 0:
                        self.state_cache.save(shows_data)
            self.state_cache.save(shows_data)
        else:
            print("[+] Show metadata is up to date.")

        # Stage 2: Watched Episodes (Matching IDs to S/E)
        to_fetch_watched = []
        for sid in base_list:
            str_sid = str(sid)
            # Fetch if missing OR if empty list (but show has history)
            watched_count = base_list[str_sid].get('watchedEpisodes', 0)
            if str_sid not in episodes_data or (not episodes_data[str_sid] and watched_count > 0):
                to_fetch_watched.append(sid)

        if to_fetch_watched:
            print(f"[*] Stage 2: Syncing watched episodes for {len(to_fetch_watched)} shows...")
            for show_id in tqdm(to_fetch_watched, desc="Episodes"):
                watched_dict = self.fetch_watched_details(show_id)
                if watched_dict:
                    str_sid = str(show_id)
                    matched_eps = []
                    show_meta = shows_data.get(str_sid, {})
                    ep_map = show_meta.get('ep_map', {})
                    
                    if isinstance(watched_dict, dict):
                        for eid, info in watched_dict.items():
                            mapping = ep_map.get(str(eid))
                            if mapping:
                                matched_eps.append({
                                    's': mapping['s'],
                                    'e': mapping['e'],
                                    'date': info.get('watchDate')
                                })
                    
                    episodes_data[str_sid] = matched_eps
                    
                    if len(episodes_data) % 10 == 0:
                        self.episode_cache.save(episodes_data)
            self.episode_cache.save(episodes_data)
        else:
            print("[+] Episode history is up to date.")

        # Stage 3: IMDb Fallback (Scraper)
        to_scrape = [sid for sid in base_list if not shows_data.get(str(sid), {}).get('imdb_id') and not self.cache.get(sid)]
        if to_scrape:
            print(f"[*] Stage 3: Scraping missing IMDb IDs for {len(to_scrape)} shows...")
            for show_id in tqdm(to_scrape, desc="Scraping"):
                imdb_id = self.scraper.get_imdb_id(show_id)
                if imdb_id:
                    self.cache.set(show_id, imdb_id)

        # Stage 4: CSV Export
        export_data = []
        active_ids = sorted(base_list.keys(), key=int)
        
        total_rows = 0
        for sid in active_ids:
            str_sid = str(sid)
            watched_eps = episodes_data.get(str_sid, [])
            total_rows += len(watched_eps)
            
            # Only add a watchlist row if it's 'later' AND we haven't watched any episodes
            if shows_data.get(str_sid, {}).get('watchStatus') == 'later' and not watched_eps:
                total_rows += 1
        
        if total_rows == 0:
            print("[-] No items to export.")
            return

        print(f"[*] Stage 4: Exporting {total_rows} items to CSV...")
        pbar = tqdm(total=total_rows, desc="Exporting")
        
        current_time_iso = datetime.now().strftime("%Y-%m-%dT12:00:00.000Z")

        for show_id_int in active_ids:
            show_id = str(show_id_int)
            meta = shows_data.get(show_id, {})
            title = meta.get('title')
            imdb_id = meta.get('imdb_id') or self.cache.get(show_id)
            rating = (meta.get('rating', 0) * 2) if meta.get('rating') else ''
            watched_eps = episodes_data.get(show_id, [])
            
            # Episodes
            for ep in watched_eps:
                watched_at = ""
                if ep.get('date'):
                    try:
                        dt = datetime.strptime(ep['date'], "%d.%m.%Y")
                        watched_at = dt.strftime("%Y-%m-%dT12:00:00.000Z")
                    except ValueError:
                        pass
                
                export_data.append({
                    'imdb_id': imdb_id or '',
                    'title': title,
                    'type': 'episode',
                    'season': ep.get('s', ''),
                    'episode': ep.get('e', ''),
                    'watched_at': watched_at,
                    'watchlisted_at': watched_at,
                    'rating': rating
                })
                pbar.update(1)
            
            # Watchlist (Only if later AND no episodes)
            if meta.get('watchStatus') == 'later' and not watched_eps:
                export_data.append({
                    'imdb_id': imdb_id or '',
                    'title': title,
                    'type': 'show',
                    'season': '',
                    'episode': '',
                    'watched_at': '',
                    'watchlisted_at': current_time_iso,
                    'rating': ''
                })
                pbar.update(1)
        pbar.close()

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['imdb_id', 'title', 'type', 'season', 'episode', 'watched_at', 'watchlisted_at', 'rating']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in export_data:
                writer.writerow(row)

        print(f"[+] Done! Saved to {csv_filename}")

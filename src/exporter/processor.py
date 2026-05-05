import csv
import time
import requests
from datetime import datetime
from tqdm import tqdm

class DataProcessor:
    def __init__(self, session, scraper, cache, state_cache, episode_cache, ep_imdb_cache):
        self.session = session
        self.scraper = scraper
        self.cache = cache # IMDb cache
        self.state_cache = state_cache # Show metadata cache
        self.episode_cache = episode_cache # Watched episodes cache
        self.ep_imdb_cache = ep_imdb_cache # Episode-level IMDb ID cache

    def fetch_imdb_episode_ids(self, show_imdb_id, season):
        """Fetch episode IDs for a specific season from imdbapi.dev with pagination support"""
        base_url = f"https://api.imdbapi.dev/titles/{show_imdb_id}/episodes?season={season}&pageSize=50"
        mapping = {}
        next_page_token = None
        pages_fetched = 0
        max_pages = 10 # Safety limit

        while pages_fetched < max_pages:
            url = base_url
            if next_page_token:
                url += f"&pageToken={next_page_token}"
            
            try:
                time.sleep(0.5)
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for ep in data.get('episodes', []):
                        ep_num = ep.get('episodeNumber')
                        ep_id = ep.get('id')
                        if ep_num is not None and ep_id:
                            mapping[str(ep_num)] = ep_id
                    
                    next_page_token = data.get('nextPageToken')
                    pages_fetched += 1  # BUG-002: increment unconditionally so loop truly stops at max_pages
                    if not next_page_token:
                        break
                else:
                    break
            except Exception as e:
                print(f"[-] Error fetching episodes for {show_imdb_id} S{season} (page {pages_fetched+1}): {e}")
                break
        
        return mapping if mapping else None

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

    def process_all(self, csv_filename, limit=None, split_size=None):
        # 1. Load Caches
        shows_data = self.state_cache.load() or {}
        episodes_data = self.episode_cache.load() or {}
        
        # 2. Sync Show List
        base_list_full = self.fetch_show_list()
        if not base_list_full:
            print("[-] Failed to fetch show list.")
            return

        # BUG-003/BUG-008: normalise all keys to str up-front so every subsequent
        # lookup (str_sid, active_ids, etc.) is consistent and type-safe.
        base_list_full = {str(k): v for k, v in base_list_full.items()}

        # Apply limit if set
        if limit and isinstance(limit, int):
            print(f"[*] Applying export limit: {limit} shows.")
            # Sort by numeric value for deterministic behaviour
            limited_ids = sorted(base_list_full.keys(), key=int)[:limit]
            base_list = {sid: base_list_full[sid] for sid in limited_ids}
        else:
            base_list = base_list_full

        # Summary of statuses (from base_list)
        stats = {}
        for s in base_list.values():
            status = s.get('watchStatus', 'unknown')
            stats[status] = stats.get(status, 0) + 1
        print(f"[*] Library summary: {stats}")

        # Stage 1: Show Metadata (Title, IMDb, Episode Map)
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
                    # Create a lean version of metadata
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
                        if imdb_str.startswith('tt'):
                            num_part = imdb_str[2:]
                            imdb_id = f"tt{num_part.zfill(7)}"
                        else:
                            imdb_id = f"tt{imdb_str.zfill(7)}"
                    
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
            # Fetch if missing
            if str_sid not in episodes_data:
                to_fetch_watched.append(sid)

        if to_fetch_watched:
            print(f"[*] Stage 2: Syncing watched episodes for {len(to_fetch_watched)} shows...")
            for show_id in tqdm(to_fetch_watched, desc="Episodes"):
                str_sid = str(show_id)
                watched_dict = self.fetch_watched_details(show_id)
                matched_eps = []

                if watched_dict and isinstance(watched_dict, dict):
                    show_meta = shows_data.get(str_sid, {})
                    ep_map = show_meta.get('ep_map', {})
                    for eid, info in watched_dict.items():
                        mapping = ep_map.get(str(eid))
                        if mapping:
                            matched_eps.append({
                                's': mapping['s'],
                                'e': mapping['e'],
                                'date': info.get('watchDate'),
                                'rating': info.get('rating')
                            })
                
                # Always save str_sid to episodes_data (even as empty list []) 
                # to mark as "fetched" and prevent Stage 2 re-sync loop.
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

        # Stage 3.5: Episode IMDb ID Sync
        ep_imdb_mapping = self.ep_imdb_cache.load() or {}
        required_seasons = {} # {show_imdb_id: set(seasons)}
        debug_count = 0
        
        for sid in base_list:
            str_sid = str(sid)
            show_imdb_id = shows_data.get(str_sid, {}).get('imdb_id') or self.cache.get(sid)
            if not show_imdb_id:
                continue
            
            watched_eps = episodes_data.get(str_sid, [])
            for ep in watched_eps:
                s = str(ep.get('s'))
                e = str(ep.get('e'))
                # If season NOT in cache, we definitely need it.
                # If season IS in cache, we don't re-fetch even if episode 'e' is missing,
                # because an empty or partial mapping means the API didn't have that episode.
                if show_imdb_id not in ep_imdb_mapping or s not in ep_imdb_mapping[show_imdb_id]:
                    if show_imdb_id not in required_seasons:
                        required_seasons[show_imdb_id] = set()
                    
                    if s not in required_seasons[show_imdb_id]:
                        required_seasons[show_imdb_id].add(s)
                        if debug_count < 5:
                            title = shows_data.get(str_sid, {}).get('title', 'Unknown')
                            # print(f"[DEBUG] Season {s} required for '{title}' (IMDb: {show_imdb_id}). Episode {e} not in cache.")
                            debug_count += 1

        if required_seasons:
            total_seasons = sum(len(s) for s in required_seasons.values())
            print(f"[*] Stage 3.5: Syncing episode IMDb IDs for {total_seasons} seasons...")
            pbar = tqdm(total=total_seasons, desc="Syncing IDs")
            for i, (show_imdb_id, seasons) in enumerate(required_seasons.items()):
                if show_imdb_id not in ep_imdb_mapping:
                    ep_imdb_mapping[show_imdb_id] = {}
                for s in seasons:
                    mapping = self.fetch_imdb_episode_ids(show_imdb_id, s)
                    # Always update mapping for the season to prevent re-sync loop,
                    # even if mapping is empty (e.g., API has no data for this season).
                    if mapping is not None:
                        ep_imdb_mapping[show_imdb_id][s] = mapping
                    elif s not in ep_imdb_mapping[show_imdb_id]:
                        # Mark as fetched with empty dict if not already present
                        ep_imdb_mapping[show_imdb_id][s] = {}
                    pbar.update(1)
                # BUG-007: save every 10 shows (not every show) to reduce I/O
                if (i + 1) % 10 == 0:
                    self.ep_imdb_cache.save(ep_imdb_mapping)
            self.ep_imdb_cache.save(ep_imdb_mapping)  # final save
            pbar.close()

        # Stage 4: CSV Export
        export_data = []
        active_ids = sorted(base_list.keys(), key=int)
        
        total_rows = 0
        skipped_episodes = 0
        for sid in active_ids:
            str_sid = str(sid)
            watched_eps = episodes_data.get(str_sid, [])
            total_rows += len(watched_eps)

            # BUG-004: all zero-episode shows get a fallback row in the export loop,
            # not only 'later' ones — count them all to keep the progress bar accurate
            # and avoid a premature early-exit when only non-'later' shows are present.
            if not watched_eps:
                total_rows += 1

        if total_rows == 0:
            print("[-] No items to export.")
            return

        print(f"[*] Stage 4: Exporting {total_rows} items to CSV...")
        pbar = tqdm(total=total_rows, desc="Exporting")
        
        # BUG-005: use actual UTC time instead of a hardcoded noon placeholder
        from datetime import timezone
        current_time_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # BUG-008: active_ids elements are already strings (keys of base_list);
        # renamed loop variable to avoid misleading '_int' suffix.
        for show_id in active_ids:
            meta = shows_data.get(show_id, {})
            show_imdb_id = meta.get('imdb_id') or self.cache.get(show_id)
            # BUG-010: guard explicitly against None (not just falsy); cast to int to
            # prevent floats (e.g. 2.5 * 2 = 5.0) from appearing in the CSV.
            _sr = meta.get('rating')
            show_rating = int(_sr * 2) if _sr is not None and _sr != 0 else ''
            watched_eps = episodes_data.get(show_id, [])
            
            # Episodes
            for ep in watched_eps:
                s = str(ep.get('s'))
                e = str(ep.get('e'))
                ep_imdb_id = ep_imdb_mapping.get(show_imdb_id, {}).get(s, {}).get(e)

                if not ep_imdb_id:
                    # BUG-006: emit a warning so silent scraper/API failures are visible
                    skipped_episodes += 1
                    pbar.update(1)
                    continue

                watched_at = ""
                if ep.get('date'):
                    try:
                        dt = datetime.strptime(ep['date'], "%d.%m.%Y")
                        watched_at = dt.strftime("%Y-%m-%dT12:00:00Z")
                    except ValueError:
                        pass

                # BUG-010: same int-cast + None guard as show rating
                _er = ep.get('rating')
                ep_rating = int(_er * 2) if _er is not None and _er != 0 else ''

                export_data.append({
                    'imdb_id': ep_imdb_id,
                    'type': 'episode',
                    'watched_at': watched_at,
                    # BUG-011: watched episodes are history items, not watchlist items;
                    # watchlisted_at must be empty for episode rows per Trakt CSV spec.
                    'watchlisted_at': '',
                    'rating': ep_rating,
                    'rated_at': watched_at if ep_rating else ''
                })
                pbar.update(1)
            
            # Fallback for shows with no mapped episodes
            if not watched_eps:
                status = meta.get('watchStatus')
                watched_at = ""
                watchlisted_at = ""
                
                if status == 'finished':
                    watched_at = 'unknown'
                else:
                    # later, watching, cancelled
                    watchlisted_at = current_time_iso

                export_data.append({
                    'imdb_id': show_imdb_id or '',
                    'type': 'show',
                    'watched_at': watched_at,
                    'watchlisted_at': watchlisted_at,
                    'rating': show_rating,
                    'rated_at': current_time_iso if (show_rating and watched_at) else ''
                })
                pbar.update(1)
        pbar.close()

        if skipped_episodes > 0:
            print(f"[!] Warning: Skipped {skipped_episodes} episodes because their IMDb IDs could not be resolved.")

        fieldnames = ['imdb_id', 'type', 'watched_at', 'watchlisted_at', 'rating', 'rated_at']

        if split_size and split_size > 0:
            print(f"[*] Splitting CSV into parts of {split_size} rows...")
            if '.' in csv_filename:
                base_name = csv_filename.rsplit('.', 1)[0]
                ext = csv_filename.rsplit('.', 1)[1]
            else:
                base_name = csv_filename
                ext = 'csv'
            
            for i in range(0, len(export_data), split_size):
                part_num = (i // split_size) + 1
                part_filename = f"{base_name}_part_{part_num}.{ext}"
                chunk = export_data[i:i + split_size]
                
                with open(part_filename, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(chunk)
                print(f"[+] Part {part_num} saved to {part_filename}")
        else:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)
            print(f"[+] Done! Saved to {csv_filename}")
        
        exported_episodes = sum(1 for row in export_data if row['type'] == 'episode')
        # Total shows = fallback 'show' rows + shows that have at least one episode
        # But easier to track unique show-level IMDb IDs before/during loop.
        # Let's count how many distinct show IDs were processed and resulted in at least one row.
        processed_shows = len(active_ids)
        print(f"[*] Export summary: {processed_shows} shows and {exported_episodes} episodes.")

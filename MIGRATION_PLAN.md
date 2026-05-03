# MyShows to Trakt Hybrid Migration Plan

## Objective
Export user show data (History and Watch Later) from MyShows to a Trakt-compatible CSV format using a hybrid approach of the legacy v1 API and targeted web scraping for IMDb metadata.

## Proposed Solution: The "Hybrid Scraper"
1.  **Auth:** Use `requests` session with username/password or a manually provided session cookie to bypass CAPTCHAs.
2.  **Data:** Fetch the base show/episode list via the legacy MyShows v1 API.
3.  **Enrichment:** Visit each MyShows show page (e.g., `/view/123/`) to scrape the **IMDb ID** for 100% accurate Trakt matching.
4.  **Transformation:**
    *   Scale ratings from 1-5 to 1-10.
    *   Map "Watch Later" status to Trakt's Watchlist.
    *   Convert dates to ISO 8601.

## Implementation Steps

### Phase 1: Modularization (src/exporter/)
- [x] Create `src/exporter/session.py`: `SessionManager` class for authentication.
- [x] Create `src/exporter/scraper.py`: `IMDbScraper` class for web scraping.
- [x] Create `src/exporter/cache.py`: `IMDbCache` and `StateCache` classes for persistence.
- [x] Create `src/exporter/processor.py`: Main processing logic, including transformation and progress tracking.
- [x] Refactor `myshows_exporter.py` to use these modules.

### Phase 2: Progress Tracking & Robustness
- [x] Implement dual-stage progress:
    1.  **Metadata Stage:** Scraping IMDb IDs (Shows).
    2.  **Export Stage:** Writing episodes to CSV (Total Episodes progress bar).
- [x] Ensure `IMDbCache` strictly reuses existing entries before attempting any network call.
- [x] Add Stage 0: Per-show detailed episode fetching with dedicated progress bar.

### Phase 3: Show Category Fixes
- [x] Update logic to handle all `watchStatus` values: `watching`, `later`, `finished`, `cancelled`.
- [x] Implement per-show detail fetching via `https://api.myshows.me/profile/shows/<id>/`.
- [x] Log a summary of shows found by status to help debug if anything is missing.

### Phase 4: Cleanup & File Organization
- [x] Update `README.md` with instructions on session cookies and new features.
- [x] Move `myshows_export.csv`, `imdb_cache.json`, and `tvshow_state_cache.json` to the `tmp/` folder.

## Verification
- [x] Verify that running `myshows_exporter.py` correctly imports from `src.exporter`.
- [x] Check `imdb_cache.json` to confirm it is updated but not overwritten.
- [x] Verify Stage 0 fetches full episode details and Stage 2 includes them in the CSV.
- [x] Final code review and modularity check.

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

### Phase 1: Environment & Auth
- [x] Add `beautifulsoup4` and `lxml` to `requirements.txt`.
- [x] Update `.env` to support `MYSHOWS_COOKIE` as an optional override for credentials.
- [x] Implement a `SessionManager` class to handle login and cookie-based auth.

### Phase 2: Data Extraction
- [x] Fetch the full user show list using `https://api.myshows.me/profile/shows/`.
- [x] Implement a caching mechanism (temporary JSON file) to store scraped IMDb IDs so the script can be resumed if interrupted.
- [x] Implement `Scraper` module:
    *   Visit `https://myshows.me/view/<show_id>/`.
    *   Extract English title and `imdb_id` from the page source.
    *   **Rate Limiting:** Add a 1.5s delay between page requests.

### Phase 3: Trakt CSV Generation
- [x] Map MyShows data to Trakt CSV columns:
    *   `imdb_id`: Extracted via scraper.
    *   `type`: `episode` for history, `show` for watchlist.
    *   `watched_at`: ISO format (defaulting to noon if time is missing).
    *   `rating`: MyShows rating * 2.
    *   `season` / `episode`: From v1 API data.
- [x] Export "Watch Later" shows as a separate CSV or combined rows with `type=show` and no `watched_at` date.

### Phase 4: Documentation & Cleanup
- [x] Update `README.md` with instructions on how to find the session cookie in Chrome/Firefox.
- [x] Add progress bars (using `tqdm`) to show scraping progress.

## Gray Areas & Pitfalls (Handled)
*   **Blocked Requests:** Solved by rate-limiting and User-Agent spoofing.
*   **Missing IMDb IDs:** Fallback to `title` + `year` matching if a show lacks an IMDb link.
*   **API v1 Limitations:** Used only for the initial list; metadata is enriched via scraping.

## Verification
- [x] Run script for a single show and verify CSV output. (Verified scraping logic against public page).
- [x] Verify `imdb_id` extraction works for a known show. (Verified `tt33204697` for show `91074`).
- [ ] Final run: Generate `myshows_export.csv` and verify it contains both episodes and "Watch Later" items.

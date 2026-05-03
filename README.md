# MyShows to Trakt Exporter

A modular Python tool to export your MyShows.me library (Watch History and Watchlist) to a Trakt-compatible CSV format.

## Features
*   **Hybrid Sync:** Uses MyShows v1 API for data and web scraping as a fallback for missing IMDb IDs.
*   **Intelligent Caching:** 
    *   `tmp/tvshow_state_cache.json`: Stores high-level show metadata.
    *   `tmp/tvshow_episode_cache.json`: Stores detailed watched episode history.
    *   `tmp/imdb_cache.json`: Stores scraped/matched IMDb IDs.
*   **Incremental Updates:** Only fetches new or updated data from the API.
*   **Multiple Auth Methods:** Login via credentials or manual session cookie override.

## Setup
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment:**
    Create a `.env` file:
    ```env
    MYSHOWS_USERNAME=your_username
    MYSHOWS_PASSWORD=your_password
    # Optional: PHPSESSID=your_id (if login is blocked)
    MYSHOWS_COOKIE=""
    ```

## Usage
Run the exporter:
```bash
python myshows_exporter.py
```
The final CSV will be saved to `tmp/myshows_export.csv`.

## Internal Documentation
*   [Documentation Overview](docs/README.md): Overview of all technical documentation.
*   [MyShows API Guide](docs/myshow/README.md): Detailed guide to the legacy v1 endpoints used.
*   [Migration Plan](MIGRATION_PLAN.md): Technical roadmap and implementation status.

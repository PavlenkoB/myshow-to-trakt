# MyShows to Trakt Exporter

[![GitHub CI](https://github.com/PavlenkoB/myshow-to-trakt/actions/workflows/ci.yml/badge.svg)](https://github.com/PavlenkoB/myshow-to-trakt/actions/workflows/ci.yml)
[![pipeline status](https://gitlab.com/PavlenkoB/myshow-to-trakt/badges/main/pipeline.svg)](https://gitlab.com/PavlenkoB/myshow-to-trakt/-/commits/main)
[![coverage report](https://gitlab.com/PavlenkoB/myshow-to-trakt/badges/main/coverage.svg)](https://gitlab.com/PavlenkoB/myshow-to-trakt/-/commits/main)

A modular Python tool to export your MyShows.me library (Watch History and Watchlist) to a Trakt-compatible CSV format.

## Features
*   **Hybrid Sync:** Uses MyShows v1 API for data and web scraping as a fallback for missing IMDb IDs.
*   **Data Integrity:** 
    *   **IMDb Padding:** Automatically ensures all IMDb IDs are `tt` prefixed and zero-padded to 7 digits (e.g., `tt0439100`).
    *   **Accurate Ratings:** Correctly scales MyShows ratings (1-5) to Trakt (1-10) per episode.
*   **Intelligent Caching:** 
    *   `tmp/tvshow_state_cache.json`: Stores high-level show metadata.
    *   `tmp/tvshow_episode_cache.json`: Stores detailed watched episode history.
    *   `tmp/imdb_cache.json`: Stores scraped/matched IMDb IDs.
*   **Incremental Updates:** Only fetches new or updated data from the API.
*   **Multiple Auth Methods:** Login via credentials or manual session cookie override.

## Setup
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/PavlenkoB/myshow-to-trakt.git
    cd myshow-to-trakt
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```env
    MYSHOWS_USERNAME=your_username
    MYSHOWS_PASSWORD=your_password
    # Optional: manual session cookie if login is blocked by CAPTCHA
    MYSHOWS_COOKIE="PHPSESSID=your_id"
    # Optional settings
    EXPORT_LIMIT=50
    CSV_SPLIT_SIZE=1000
    ```

## Usage
Run the main exporter script:
```bash
python src/myshows_exporter.py
```
The final CSV will be saved to `tmp/myshows_export.csv`. If `CSV_SPLIT_SIZE` is set, it will automatically split the export into multiple parts.

## Testing
This project uses `pytest` for unit testing.
To run the test suite:
```bash
export PYTHONPATH=.
pytest tests/ --cov=src
```

## Internal Documentation
*   [Documentation Overview](docs/README.md): Overview of all technical documentation.
*   [MyShows API Guide](docs/myshow/README.md): Detailed guide to the legacy v1 endpoints used.
*   [Migration Plan](MIGRATION_PLAN.md): Technical roadmap and implementation status.
*   [Trakt CSV Import Guide](docs/trakt_csv_instruction.md): Requirements for importing data into Trakt.

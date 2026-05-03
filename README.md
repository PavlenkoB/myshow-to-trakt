# MyShows to Trakt Exporter

A tool to export your watched shows history from MyShows to a CSV format compatible with Trakt import tools.

## Features

- **Hybrid Scraper:** Combines MyShows v1 API for data structure and web scraping for accurate IMDb IDs.
- **IMDb ID Enrichment:** Automatically visits show pages to find IMDb links, ensuring 100% matching on Trakt.
- **Watchlist Support:** Exports both watch history (episodes) and "Watch Later" items (shows).
- **Persistent Cache:** Saves scraped IMDb IDs to `imdb_cache.json` to resume interrupted exports.
- **Robust Auth:** Supports traditional login and session cookie overrides to bypass CAPTCHAs.

## Setup

1.  Clone the repository.
2.  Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

3.  Create a `.env` file based on the template:
    ```env
    MYSHOWS_USERNAME=your_username
    MYSHOWS_PASSWORD=your_password
    # Optional: If login fails due to CAPTCHA, provide your PHPSESSID from your browser
    MYSHOWS_COOKIE="PHPSESSID=your_session_id_here"
    ```

### How to get `PHPSESSID`
1. Log in to [myshows.me](https://myshows.me) in your browser.
2. Open Developer Tools (F12 or Cmd+Opt+I).
3. Go to the **Application** (Chrome) or **Storage** (Firefox) tab.
4. Look for **Cookies** and find `PHPSESSID`.

## Usage

Run the exporter:
```bash
python myshows_exporter.py
```

The script will generate `myshows_export.csv`.

## Importing to Trakt

The generated CSV is compatible with the custom CSV importer at [trakt.tv/import](https://trakt.tv/import) or standard Python import tools like [xbgmsharp/trakt](https://github.com/xbgmsharp/trakt).

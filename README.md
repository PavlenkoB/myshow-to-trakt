# MyShows to Trakt Exporter

[![GitHub CI](https://github.com/PavlenkoB/myshow-to-trakt/actions/workflows/ci.yml/badge.svg)](https://github.com/PavlenkoB/myshow-to-trakt/actions/workflows/ci.yml)
[![pipeline status](https://gitlab.com/PavlenkoB/myshow-to-trakt/badges/main/pipeline.svg)](https://gitlab.com/PavlenkoB/myshow-to-trakt/-/commits/main)
[![coverage report](https://gitlab.com/PavlenkoB/myshow-to-trakt/badges/main/coverage.svg)](https://gitlab.com/PavlenkoB/myshow-to-trakt/-/commits/main)

A modular Python tool to export your MyShows.me library (Watch History and Watchlist) to a Trakt-compatible CSV format.

## Features

- **4-Stage Pipeline** — metadata sync → watched episode sync → IMDb ID resolution → CSV export.
- **Hybrid IMDb Resolution:**
  - Pulls `imdbId` directly from the MyShows API where available.
  - Falls back to web scraping the MyShows show page (`/view/<id>/`) if the API omits it.
  - Resolves per-episode IMDb IDs from [imdbapi.dev](https://api.imdbapi.dev) with pagination support.
- **Data Integrity:**
  - IMDb IDs are always `tt`-prefixed and zero-padded to ≥ 7 digits (e.g., `tt0439100`).
  - Ratings are scaled from MyShows 1–5 → Trakt 1–10 (integer, no floats in CSV).
  - Dates are converted to ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
  - `watchlisted_at` is empty for episode (history) rows; populated only for watchlist shows.
- **Intelligent Caching** — all state lives in `tmp/`, nothing is re-fetched if already cached:
  - `tmp/tvshow_state_cache.json` — show-level metadata and episode map.
  - `tmp/tvshow_episode_cache.json` — per-show watched episode history.
  - `tmp/imdb_cache.json` — scraped IMDb IDs (global fallback).
  - `tmp/episode_imdb_cache.json` — per-season episode IMDb IDs from imdbapi.dev.
- **Incremental Updates** — only shows/episodes absent from cache are fetched.
- **Multiple Auth Methods** — username/password (MD5) or a manually supplied session cookie; cookie validity is verified against the API before the export starts.
- **CSV Splitting** — large exports can be split into multiple files via `CSV_SPLIT_SIZE`.

## Project Structure

```
myshow-to-trakt/
├── src/
│   ├── myshows_exporter.py      # Entry point
│   └── exporter/
│       ├── session.py           # Auth: credentials or cookie (with verification)
│       ├── scraper.py           # IMDb fallback scraper
│       ├── cache.py             # IMDbCache and StateCache
│       └── processor.py        # 4-stage pipeline + CSV export
├── tests/                       # pytest suite (unit, mocked — 12 tests)
├── docs/                        # API reference and Trakt CSV spec
├── tmp/                         # Runtime caches and output CSV (git-ignored)
└── .env                         # Credentials and runtime config
```

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PavlenkoB/myshow-to-trakt.git
   cd myshow-to-trakt
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   pip install -r requirements.txt
   ```

3. **Configure environment variables** — create a `.env` file in the project root:
   ```env
   # Auth — use credentials OR a cookie (cookie takes priority if set)
   MYSHOWS_USERNAME=your_username
   MYSHOWS_PASSWORD=your_password

   # Optional: supply a valid session cookie if login is blocked by CAPTCHA.
   # The tool verifies the cookie against the API before starting the export
   # and exits with a clear error message if the cookie is expired.
   MYSHOWS_COOKIE="PHPSESSID=your_session_id"

   # Optional: limit the number of shows processed (useful for dry-runs)
   EXPORT_LIMIT=50

   # Optional: split the output CSV into parts of N rows each
   CSV_SPLIT_SIZE=1000
   ```

## Usage

```bash
source .venv/bin/activate
python src/myshows_exporter.py
```

The export is written to `tmp/myshows_export.csv`.
If `CSV_SPLIT_SIZE` is set, the output is split into `tmp/myshows_export_part_1.csv`, `_part_2.csv`, etc.

### Pipeline Stages

| Stage | What it does |
|-------|--------------|
| **1 — Metadata** | Fetches show titles, IMDb IDs, and episode season/number maps from the MyShows API. Cached in `tvshow_state_cache.json`. |
| **2 — Episodes** | Fetches per-show watched episode lists and maps episode IDs to S/E numbers. Cached in `tvshow_episode_cache.json`. |
| **3 — IMDb Fallback** | Scrapes the MyShows web page for any show still missing an IMDb ID. Cached in `imdb_cache.json`. |
| **3.5 — Episode IMDb IDs** | Resolves individual episode IMDb IDs season-by-season via imdbapi.dev (paginated). Cached in `episode_imdb_cache.json`. |
| **4 — CSV Export** | Applies rating scaling, date formatting, and watchlist fallback logic; writes the final CSV. |

### Watchlist Fallback Logic

Shows with **zero mapped episodes** get a single `type=show` row:

| `watchStatus` | CSV behaviour |
|---------------|---------------|
| `finished` | `watched_at=unknown` — marks the whole show as watched |
| `later` / `watching` / `cancelled` | `watchlisted_at=<now>` — adds the show to the Watchlist |

## Testing

```bash
source .venv/bin/activate
export PYTHONPATH=.
pytest tests/ -v --cov=src
```

The suite covers cache, scraper, session, and processor logic with fully mocked HTTP calls — 12 tests, no network access required.

## Troubleshooting

- **"Failed to fetch show list"** — Your session has expired. Re-generate `MYSHOWS_COOKIE` from browser DevTools (Application → Cookies → `myshows.me`).
- **"Cookie auth failed: server returned 403"** — Cookie is present but rejected by the API. Refresh it in `.env`.
- **Episodes skipped (IMDb ID not resolved)** — The episode exists in MyShows but imdbapi.dev has no record for that season yet. Re-running later will resolve it automatically from cache.
- **Large libraries** — Set `EXPORT_LIMIT=10` to validate the output before committing to a full run.

## Internal Documentation

- [Documentation Overview](docs/README.md) — Overview of all technical documentation.
- [MyShows API Guide](docs/myshow/README.md) — Detailed guide to the legacy v1 endpoints used.
- [Migration Plan](MIGRATION_PLAN.md) — Technical roadmap and implementation status.
- [Trakt CSV Import Guide](docs/trakt_csv_instruction.md) — Requirements for importing data into Trakt.

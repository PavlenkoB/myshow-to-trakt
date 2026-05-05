# AI Agent Directives

These instructions are for AI development tools interacting with this codebase.

## Project Scope
* **Purpose:** Maintain and optimize the MyShows to Trakt data migration tool.
* **Stack:** Python 3, `requests`, `beautifulsoup4`, `tqdm`.
* **Standard:** Follow the conventions defined in [GEMINI.md](GEMINI.md).

## Agent Constraints
* Format all outputs and documentation using bullet points.
* Keep explanations and code changes short and concise.
* Minimize third-party dependencies; rely on standard Python libraries when possible.
* Handle API errors and edge cases (e.g., missing dates, failed auth) silently but safely.
* Do not introduce heavy architectural patterns for simple scripts.

## Project Standards & Conventions

### 1. Data Processing
* **IMDb IDs:** Must always be prefixed with `tt` and padded to at least 7 digits (e.g., `tt0439100`). Episode-level IDs are resolved via `imdbapi.dev`.
* **Ratings:** Scale conversion from MyShows (1-5) to Trakt (1-10) is handled by multiplying by 2.
* **Timestamps:** All timestamps must follow ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`).

### 2. CSV Export Format
* The export follows the official Trakt CSV import schema.
* **Columns:** `imdb_id`, `type`, `watched_at`, `watchlisted_at`, `rating`, `rated_at`.
* **Fallback Logic:** For shows with 0 mapped episodes, a `type=show` entry is created. If status is `finished`, it marks the whole show as watched (`watched_at=unknown`). Otherwise (`later`, `watching`, `cancelled`), it adds it to the Watchlist (`watchlisted_at=now`).
* **Watchlisted At:** For episodes, `watchlisted_at` matches `watched_at`. For watchlist shows, it defaults to the current date/time.
* **Rated At:** For episodes with a rating, `rated_at` matches `watched_at`.

### 3. Caching & Persistence
* All caches and temporary data reside in `tmp/`.
* `imdb_cache.json`: Global fallback for scraped IMDb IDs.
* `tvshow_state_cache.json`: Show-level metadata (includes `ep_map`).
* `tvshow_episode_cache.json`: Per-show watched episode history.

### 4. Configuration
* Use `.env` for all sensitive credentials and runtime limits.
* `EXPORT_LIMIT`: Limits the number of shows processed (useful for debugging).
* `CSV_SPLIT_SIZE`: Splits the final CSV into multiple parts (e.g., `_part_1.csv`).

## Reference Documentation
* [Documentation Overview](docs/README.md): Entry point for all technical documentation.
* [MyShows API Endpoints](docs/myshow/README.md): Detailed guide to the legacy v1 endpoints used by this tool.
* [Migration Plan](MIGRATION_PLAN.md): Roadmap for data export and import strategies.
* [Trakt CSV Import Instructions](docs/trakt_csv_instruction.md): Format requirements for importing data into Trakt via CSV.

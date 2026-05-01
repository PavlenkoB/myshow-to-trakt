# MyShows to Trakt Migration Plan

## Objective
Migrate user show data from MyShows to Trakt using a Python script to export data to CSV, which can then be imported into Trakt.

## Key Links
*   **MyShows API:** The legacy v1 API at `https://api.myshows.me/profile/shows/` is used for fetching user data.
*   **Trakt Import Tool:** [xbgmsharp/trakt](https://github.com/xbgmsharp/trakt) (or similar forks like `trakt-csv-scripts`) is the standard Python tool for importing CSVs to Trakt.

## Implementation Steps
- [x] Refactor credentials to use a secure `.env` file.
- [x] Ensure `python-dotenv` is listed in `requirements.txt`.
- [ ] **Data Validation & Formatting:** Ensure the generated CSV `myshows_export.csv` strictly matches the column format expected by the `trakt-csv-import` scripts (typically requiring specific column headers like `title`, `season`, `episode`, `watched_at`).
- [ ] **Error Handling:** Add robust exception handling for network requests (e.g., `requests.exceptions.RequestException`) and API authentication failures.
- [ ] **Documentation:** Create or update `README.md` in the project root to include setup instructions and the links to the MyShows API and the Trakt Python import tool.
- [x] **Write Plan to Root:** Copy this plan to a file in the project root directory (`MIGRATION_PLAN.md`).

## Verification
*   Run the script locally to ensure it successfully generates a valid `myshows_export.csv`.
*   Verify that `README.md` contains the requested links.

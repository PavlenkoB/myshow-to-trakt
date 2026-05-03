# Trakt CSV Import Instructions

This guide describes the updated format for importing your TV show data into Trakt.tv using the official CSV importer.

## Supported Column Headers

To ensure accurate matching and metadata processing, your CSV should use the following headers. The ID column must be prefixed with the service name (e.g., `imdb_id`).

| Header | Description | Required | Example |
| :--- | :--- | :--- | :--- |
| `imdb_id` | The ID of the item. Can also be `trakt_id`, `tmdb_id`, or `tvdb_id`. | Required | `tt0439100` |
| `type` | Entry type: `movie`, `show`, `season`, or `episode`. | Recommended | `episode` |
| `watched_at` | Date and time the item was watched (ISO 8601). Can be `unknown`. | For History | `2024-12-17T12:00:00Z` |
| `watchlisted_at` | Date and time the item was added to your watchlist (ISO 8601). | For Watchlist | `2024-12-17T12:00:00Z` |
| `rating` | Your rating for the item (1–10). | Optional | `10` |
| `rated_at` | Date and time the item was rated (ISO 8601). Requires `rating`. | Optional | `2024-12-17T12:00:00Z` |
| `title` | Title of the show (used as fallback for matching). | Recommended | `Breaking Bad` |
| `season` | Season number (numeric). | For episodes | `1` |
| `episode` | Episode number (numeric). | For episodes | `5` |

## Key Requirements

### 1. IDs
The ID should be prefixed with the service name. For example, if you are using IMDb IDs, the column header must be `imdb_id`. Trakt supports:
*   `trakt_id`
*   `imdb_id`
*   `tmdb_id`
*   `tvdb_id` (TV shows only)

### 2. Timestamps
All dates must follow the **ISO 8601** standard (`YYYY-MM-DDTHH:MM:SSZ`).
*   **watched_at:** Can have `unknown` as a value if the date is not known. Can be omitted if only adding to your watchlist.
*   **watchlisted_at:** Can be omitted if only marking as watched.
*   **rated_at:** Only parsed if a `rating` is also present.

### 3. History vs. Watchlist
*   **History:** Items with a `watched_at` value are added to your history.
*   **Watchlist:** Items with a `watchlisted_at` value (and no `watched_at`) are added to your watchlist.

## Sample CSV Structure

```csv
imdb_id,type,watched_at,watchlisted_at,rating,rated_at
tt0068646,movie,2024-10-25T20:00:00Z,2024-10-01T10:00:00Z,7,2024-10-25T21:00:00Z
tt15239678,movie,,2024-04-30T11:00:00Z,,
tt4281724,movie,2024-01-12T02:00:00Z,,,
```

## How to Import
1.  Go to [trakt.tv/import](https://trakt.tv/import).
2.  Choose the **CSV** import option.
3.  Upload your generated CSV file.
4.  Review the matched items and confirm the import.

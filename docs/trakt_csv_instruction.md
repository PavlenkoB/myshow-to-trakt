# Trakt CSV Import Instructions

This guide describes the expected format for importing your TV show data into Trakt.tv using the official CSV importer.

## Supported Column Headers

To ensure accurate matching and metadata processing, your CSV should use the following headers. The order of columns does not matter.

| Header           | Description                                                          | Required              | Example                |
|:-----------------|:---------------------------------------------------------------------|:----------------------|:-----------------------|
| `imdb_id`        | IMDb ID (starts with `tt`). Best for 100% accuracy.                  | Highly Recommended    | `tt0439100`            |
| `type`           | The type of entry: `show`, `season`, or `episode`.                   | Highly Recommended    | `episode`              |
| `title`          | Title of the show.                                                   | Recommended           | `Breaking Bad`         |
| `season`         | Season number (numeric).                                             | Required for episodes | `1`                    |
| `episode`        | Episode number (numeric).                                            | Required for episodes | `5`                    |
| `watchlisted_at` | Date and time the item was added to your watchlist. ISO 8601 format. | For History           | `2024-12-17T12:00:00Z` |
| `watched_at`     | Watch timestamp in ISO 8601 format.                                  | For History           | `2024-12-17T12:00:00Z` |
| `rating`         | Your rating on a scale of 1–10.                                      | Optional              | `10`                   |

## Key Requirements

### 1. Timestamps

All dates (like `watched_at`) must follow the **ISO 8601** standard.

* **Format:** `YYYY-MM-DDTHH:MM:SSZ`
* **Note:** If the specific time is unknown, the exporter defaults to `12:00:00.000Z` (noon UTC).

### 2. ID Priority

Trakt uses multiple IDs for matching. If multiple are provided, it usually prioritizes them as follows:
`trakt_id` > `imdb_id` > `tmdb_id` > `tvdb_id`.

### 3. History vs. Watchlist

* **History Import:** Any row containing a value in the `watched_at` column will be imported into your **History**.
* **Watchlist Import:** Rows where `type` is `show` and `watched_at` is empty will be added to your **Watchlist**.

## Sample CSV Structure

```csv
imdb_id,type,watched_at,watchlisted_at,rating,rated_at
tt0068646,movie,2024-10-25T20:00:00Z,2024-10-01T10:00:00Z,7,2024-10-25T21:00:00Z
tt15239678,movie,,2024-04-30T11:00:00Z,,
tt4281724,movie,2024-01-12T02:00:00Z,,,
```

## How to Import

1. Go to [trakt.tv/import](https://trakt.tv/import).
2. Choose the **CSV** import option.
3. Upload your `tmp/myshows_export.csv`.
4. Review the matched items and confirm the import.

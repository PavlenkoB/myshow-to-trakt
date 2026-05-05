<note>
  <summary>Trakt official CSV importer requires episode-level IDs for watch history matching.</summary>
  <tags>#domain #trakt #csv-import</tags>
  <context>
    When importing TV show watch history into Trakt via CSV, providing a Show IMDb ID (`imdb_id`) combined with `season` and `episode` columns results in "item could not be found" errors. The 2024+ Trakt VIP importer ignores the season/episode columns for matching and expects the unique ID of the specific episode.
  </context>
  <solution>
    Resolve and provide the specific IMDb ID for every episode (e.g., `tt10314540` for S01E01 of a show). The `type` column should be set to `episode`.
    Additionally, timestamps must be strict ISO 8601 without milliseconds (e.g., `2024-05-05T12:00:00Z`). Milliseconds (`.000Z`) can cause parsing failures.
  </solution>
  <constraints>
    - Always use episode-level IMDb IDs for `type: episode` rows.
    - Omit milliseconds from ISO 8601 timestamps.
    - Remove `season` and `episode` columns as they are no longer supported for matching.
  </constraints>
</note>

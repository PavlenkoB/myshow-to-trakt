<note>
  <summary>Handling limitations and caching for episode ID resolution via imdbapi.dev.</summary>
  <tags>#architecture #api #imdb</tags>
  <context>
    Resolving thousands of episode IDs (e.g., 17k+) from a show ID requires external API lookups. Using `https://api.imdbapi.dev/` introduces rate-limiting risks and specific parameter constraints.
  </context>
  <solution>
    Implement a per-season caching layer (`episode_imdb_cache.json`) to store `{season: {episode: imdb_id}}` mappings. This minimizes redundant network calls.
    The `imdbapi.dev` `/titles/{id}/episodes` endpoint has a strict `pageSize` limit of 50; values > 50 return a `400 Bad Request`.
  </solution>
  <constraints>
    - Set `pageSize` to 50 or less for `imdbapi.dev` episode queries.
    - Implement persistent caching for resolved episode IDs to avoid IP blocks.
    - Add a delay (e.g., 0.5s) between API calls to respect external rate limits.
  </constraints>
</note>

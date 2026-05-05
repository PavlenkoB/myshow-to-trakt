<note>
  <summary>Nuances of the MyShows API v1 for show metadata and user history.</summary>
  <tags>#domain #myshows #api</tags>
  <context>
    The legacy MyShows API v1 has inconsistent URL patterns and numeric ID handling that can lead to 404s or metadata mismatches.
  </context>
  <solution>
    - **Trailing Slashes**: `/shows/{id}` (Public Meta) MUST NOT have a trailing slash. `/profile/shows/{id}/` (User Data) MUST have a trailing slash.
    - **ID Padding**: IMDb IDs returned as integers (e.g., `439100`) must be padded to 7 digits and prefixed (e.g., `tt0439100`) using `str(id).zfill(7)` for correct external matching.
    - **Episode Maps**: Store the mapping of internal MyShows `episodeId` to `(season, episodeNumber)` from the metadata endpoint, as the user history endpoint only returns `episodeId`.
  </solution>
  <constraints>
    - Adhere strictly to the trailing slash requirements per endpoint.
    - Always pad numeric IMDb IDs to 7 digits with `tt` prefix.
  </constraints>
</note>

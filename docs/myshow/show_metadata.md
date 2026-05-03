# Show Metadata (Public)

Used to retrieve show-level metadata and episode mapping.

*   **Endpoint:** `GET https://api.myshows.me/shows/{show_id}`
*   **Note:** No trailing slash at the end of the URL.
*   **Behavior:**
    *   Provides high-level metadata (English title, IMDb ID).
    *   Contains a full map of all episode IDs to their respective Season and Episode numbers (`ep_map`).
*   **Sample Response:**
    ```json
    {
      "title": "Secret Level",
      "imdbId": "33204697",
      "episodes": {
        "18799158": {
          "seasonNumber": 1,
          "episodeNumber": 15
        }
      }
    }
    ```

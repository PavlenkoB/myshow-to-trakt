# User Library (Show List)

Used to retrieve the full list of shows in the user's library.

*   **Endpoint:** `GET https://api.myshows.me/profile/shows/`
*   **Behavior:**
    *   Returns a dictionary where keys are show IDs.
    *   Used to identify all shows associated with the user account (Watching, Later, Finished).
*   **Sample Response:**
    ```json
    {
      "91074": {
        "title": "Secret Level",
        "watchStatus": "watching",
        "rating": 5
      }
    }
    ```

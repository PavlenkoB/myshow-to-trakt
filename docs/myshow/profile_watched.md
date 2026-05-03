# Watched Episodes (Profile)

Used to retrieve the user's interaction history for a specific show.

*   **Endpoint:** `GET https://api.myshows.me/profile/shows/{show_id}/`
*   **Note:** Requires a trailing slash at the end of the URL.
*   **Behavior:**
    *   Returns a dictionary of episodes the user has interacted with (watched or rated).
    *   Used to extract the `watchDate` for each episode to include in the Trakt history.
*   **Sample Response:**
    ```json
    {
      "18799158": {
        "id": 18799158,
        "watchDate": "17.12.2024",
        "rating": 5
      }
    }
    ```

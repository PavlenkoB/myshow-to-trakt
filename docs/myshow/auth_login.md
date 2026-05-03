# Authentication (Login)

Used to establish a session with the MyShows API.

*   **Endpoint:** `GET https://api.myshows.me/profile/login?login={login}&password={md5_password}`
*   **Parameters:**
    *   `login`: MyShows username.
    *   `password`: MD5 hash of the password.
*   **Behavior:**
    *   Returns user profile JSON on success.
    *   Sets standard HTTP session cookies (e.g., `PHPSESSID`) required for subsequent profile requests.

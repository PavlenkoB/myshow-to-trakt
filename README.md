# MyShows to Trakt Exporter

A tool to export your watched shows history from MyShows to a CSV format compatible with Trakt import tools.

## Resources

*   **MyShows API Documentation**: [https://api.myshows.me/shared/doc/](https://api.myshows.me/shared/doc/)
*   **Trakt CSV Import Tool**: [xbgmsharp/trakt](https://github.com/xbgmsharp/trakt) (Recommended Python tool for importing the generated CSV).

## Setup

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file based on the template:
    ```env
    MYSHOWS_USERNAME=your_username
    MYSHOWS_PASSWORD=your_password
    ```
4.  Run the exporter:
    ```bash
    python myshows_exporter.py
    ```

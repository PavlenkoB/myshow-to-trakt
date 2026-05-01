import requests
import hashlib
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === SETTINGS ===
USERNAME = os.getenv('MYSHOWS_USERNAME')
PASSWORD = os.getenv('MYSHOWS_PASSWORD')
CSV_FILENAME = 'myshows_export.csv'
# ================

def get_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def main():
    session = requests.Session()

    # 1. Authorization (API v1)
    login_url = f"https://api.myshows.me/profile/login?login={USERNAME}&password={get_md5(PASSWORD)}"
    auth_resp = session.get(login_url)

    if auth_resp.status_code != 200:
        print("[-] Authorization error. Check login and password.")
        return
    print("[+] Successful authorization.")

    # 2. Get profile shows list
    print("[*] Downloading shows list...")
    shows_resp = session.get("https://api.myshows.me/profile/shows/")
    shows_data = shows_resp.json()

    # 3. Prepare file for trakt-csv-import
    with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'tvdb', 'season', 'episode', 'watched_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total_episodes = 0

        # MyShows API returns a dictionary where keys are show IDs
        for show_id, show_info in shows_data.items():
            title = show_info.get('title') # English title is preferred, Trakt searches it better

            # If there are watched episodes
            if 'episodes' in show_info:
                for ep in show_info['episodes']:
                    # ep usually contains id, seasonNumber, episodeNumber, date
                    season = ep.get('seasonNumber', 1)
                    episode = ep.get('episodeNumber', 1)

                    # MyShows often provides date in 'DD.MM.YYYY' format, converting for Trakt
                    raw_date = ep.get('watchDate')
                    watched_at = ""
                    if raw_date:
                        try:
                            dt = datetime.strptime(raw_date, "%d.%m.%Y")
                            watched_at = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                        except ValueError:
                            pass # If format is different, leave empty

                    writer.writerow({
                        'title': title,
                        'tvdb': show_info.get('tvrageId', ''), # If TVRage or TVDB ID is present in MyShows database
                        'season': season,
                        'episode': episode,
                        'watched_at': watched_at
                    })
                    total_episodes += 1

    print(f"[+] Export finished! Saved {total_episodes} episodes to {CSV_FILENAME}")

if __name__ == "__main__":
    main()

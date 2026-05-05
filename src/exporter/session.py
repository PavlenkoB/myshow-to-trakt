# src/exporter/session.py
import requests
import hashlib
import os

class SessionManager:
    def __init__(self, user_agent):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def login(self, username=None, password=None, session_cookie=None):
        if session_cookie:
            print("[+] Using provided session cookie.")
            for cookie in session_cookie.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    self.session.cookies.set(name, value, domain='myshows.me')
            # BUG-009: verify the cookie is still valid before proceeding
            try:
                resp = self.session.get("https://api.myshows.me/profile/", timeout=10)
                if resp.status_code == 200:
                    return True
                print(f"[-] Cookie auth failed: server returned {resp.status_code}. Cookie may be expired.")
            except requests.RequestException as e:
                print(f"[-] Network error during cookie verification: {e}")
            return False

        if not username or not password:
            print("[-] Error: Missing credentials.")
            return False

        print(f"[*] Logging in as: {username}")
        md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        login_url = f"https://api.myshows.me/profile/login?login={username}&password={md5_password}"
        try:
            resp = self.session.get(login_url)
            if resp.status_code == 200:
                print("[+] Successful authorization.")
                return True
            print(f"[-] Auth failed: {resp.status_code}")
        except requests.RequestException as e:
            print(f"[-] Network error during login: {e}")
        return False

    def get_session(self):
        return self.session

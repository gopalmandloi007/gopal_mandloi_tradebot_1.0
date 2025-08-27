import logging
import pyotp
import requests

BASE_URL = "https://api.definedgesecurities.com"  # Main Definedge endpoint

class SessionError(Exception):
    pass

class SessionManager:
    def __init__(self, api_token, api_secret, totp_secret=None):
        self.api_token = api_token
        self.api_secret = api_secret
        self.totp_secret = totp_secret
        self.api_session_key = None
        self.susertoken = None
        self.uid = None

    def login(self, prefer_totp=True):
        """
        Performs login with API token/secret and TOTP.
        """
        if not self.api_token or not self.api_secret:
            raise SessionError("Missing API token/secret")

        otp = None
        if prefer_totp and self.totp_secret:
            otp = pyotp.TOTP(self.totp_secret).now()

        payload = {
            "api_key": self.api_token,
            "api_secret": self.api_secret,
        }
        if otp:
            payload["otp"] = otp

        url = f"{BASE_URL}/integrate/v1/session"
        resp = requests.post(url, json=payload)

        if resp.status_code != 200:
            raise SessionError(f"Login failed: {resp.text}")

        data = resp.json()
        if "data" not in data or "susertoken" not in data["data"]:
            raise SessionError(f"Unexpected response: {data}")

        self.api_session_key = data["data"]["session_key"]
        self.susertoken = data["data"]["susertoken"]
        self.uid = data["data"]["uid"]

        return data

    def is_logged_in(self):
        return bool(self.api_session_key and self.susertoken)

    def get_auth_headers(self):
        if not self.is_logged_in():
            raise SessionError("Not logged in. Please call login() first.")
        return {
            "Authorization": f"Bearer {self.api_session_key}",
            "x-session-token": self.susertoken,
        }

    def call_api(self, method, endpoint, params=None, data=None):
        """
        Generic wrapper to call Definedge APIs.
        """
        if not self.is_logged_in():
            raise SessionError("Not logged in")

        url = f"{BASE_URL}{endpoint}"
        headers = self.get_auth_headers()

        resp = requests.request(method, url, headers=headers, params=params, json=data)

        if resp.status_code != 200:
            raise SessionError(f"API call failed {resp.status_code}: {resp.text}")

        return resp.json()

import os
import pyotp
import requests
import logging
import streamlit as st

# Logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SessionError(Exception):
    pass


class SessionManager:
    def __init__(self, api_token: str, api_secret: str, totp_secret: str):
        self.api_token = api_token
        self.api_secret = api_secret
        self.totp_secret = totp_secret

        self.uid = None
        self.api_session_key = None
        self.susertoken = None

    def is_logged_in(self):
        return self.api_session_key is not None and self.susertoken is not None

    def get_auth_headers(self):
        if not self.is_logged_in():
            raise SessionError("Not logged in yet")
        return {
            "Authorization": f"Bearer {self.api_session_key}",
            "x-session-token": self.susertoken
        }

    # --------------------------
    # Login with TOTP
    # --------------------------
    def login_with_totp(self):
        try:
            otp = pyotp.TOTP(self.totp_secret).now()
            logger.debug(f"Generated TOTP: {otp}")

            # Dummy request simulation
            # TODO: replace with real API call
            if otp:
                self.uid = "demo_uid"
                self.api_session_key = "demo_api_session_key"
                self.susertoken = "demo_susertoken"
                return True
            return False
        except Exception as e:
            raise SessionError(f"TOTP login failed: {str(e)}")

    # --------------------------
    # Manual OTP Flow
    # --------------------------
    def request_otp(self):
        # Simulate otp_token generation
        otp_token = "dummy_otp_token"
        return otp_token

    def verify_otp(self, otp_token, otp_code):
        if otp_token and otp_code == "123456":  # simulation
            self.uid = "demo_uid"
            self.api_session_key = "demo_api_session_key"
            self.susertoken = "demo_susertoken"
            return True
        return False

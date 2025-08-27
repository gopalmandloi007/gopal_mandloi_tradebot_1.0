import os
from dotenv import load_dotenv
import streamlit as st

# Load local .env file
load_dotenv()

class Config:
    """Centralized config handler for local and Streamlit secrets."""

    # ---------- API KEYS ----------
    API_KEY = os.getenv("API_KEY") or st.secrets.get("API_KEY")
    API_SECRET = os.getenv("API_SECRET") or st.secrets.get("API_SECRET")

    # ---------- AUTH / LOGIN ----------
    USERNAME = os.getenv("USERNAME") or st.secrets.get("USERNAME")
    PASSWORD = os.getenv("PASSWORD") or st.secrets.get("PASSWORD")
    PIN = os.getenv("PIN") or st.secrets.get("PIN")

    # ---------- OTP / TOTP ----------
    OTP_SECRET = os.getenv("OTP_SECRET") or st.secrets.get("OTP_SECRET")   # for manual OTP
    TOTP_SECRET = os.getenv("TOTP_SECRET") or st.secrets.get("TOTP_SECRET")  # for auto-TOTP

    # ---------- FILE PATHS ----------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # root dir jaha app.py hai
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    MASTER_FILE = os.path.join(DATA_DIR, "master", "allmaster.csv")
    ERROR_LOG = os.path.join(LOG_DIR, "errors.log")
    ACTIVITY_LOG = os.path.join(LOG_DIR, "general_log", "activity.log")
    STRATEGY1_LOG = os.path.join(LOG_DIR, "strategy_1", "signals.log")

    @classmethod
    def show(cls):
        """Debug ke liye config values check karne ka helper"""
        return {
            "API_KEY": cls.API_KEY,
            "USERNAME": cls.USERNAME,
            "DATA_DIR": cls.DATA_DIR,
            "LOG_DIR": cls.LOG_DIR,
            "MASTER_FILE": cls.MASTER_FILE
        }

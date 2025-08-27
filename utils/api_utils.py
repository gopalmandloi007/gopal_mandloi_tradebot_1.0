"""
Centralized connection logic for Definedge Integrate API.

Features:
- Reuses session keys saved in .env (fast login)
- Loads credentials from Streamlit secrets or .env
- Supports OTP/TOTP generation
- Saves session keys back to .env
- Full debug logging for every step
"""

import os
import logging
from typing import Optional
from integrate import ConnectToIntegrate
import pyotp

# ----------------- Setup logger -----------------
logger = logging.getLogger("api_utils")
logger.setLevel(logging.DEBUG)  # DEBUG level
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# ----------------- Internal helpers -----------------
def _ensure_dotenv() -> str:
    from dotenv import load_dotenv, find_dotenv
    path = find_dotenv()
    if not path:
        path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(path):
            open(path, "a").close()
    load_dotenv(path)
    logger.debug(f".env loaded from: {path}")
    return path

def _save_session_keys(dotenv_path: str, uid: str, actid: str, api_session_key: str, ws_session_key: str):
    from dotenv import set_key
    set_key(dotenv_path, "INTEGRATE_UID", uid)
    set_key(dotenv_path, "INTEGRATE_ACTID", actid)
    set_key(dotenv_path, "INTEGRATE_API_SESSION_KEY", api_session_key)
    set_key(dotenv_path, "INTEGRATE_WS_SESSION_KEY", ws_session_key)
    logger.info("Session keys saved to .env")

def _get_credentials():
    api_token = api_secret = totp_secret = None

    # --- Streamlit secrets first ---
    try:
        import streamlit as st
        api_token = st.secrets.get("INTEGRATE_API_TOKEN")
        api_secret = st.secrets.get("INTEGRATE_API_SECRET")
        totp_secret = st.secrets.get("totp", {}).get("secret")
        logger.debug(f"Loaded credentials from Streamlit secrets. TOTP: {'Yes' if totp_secret else 'No'}")
    except Exception as e:
        logger.debug(f"Streamlit secrets not available: {e}")

    # --- Fallback to .env ---
    if not api_token or not api_secret:
        from dotenv import load_dotenv
        load_dotenv()
        api_token = os.getenv("INTEGRATE_API_TOKEN")
        api_secret = os.getenv("INTEGRATE_API_SECRET")
        if not totp_secret:
            totp_secret = os.getenv("TOTP_SECRET")
        logger.debug("Loaded credentials from .env")

    logger.debug(f"API Token: {bool(api_token)}, API Secret: {bool(api_secret)}, TOTP Secret: {bool(totp_secret)}")
    return api_token, api_secret, totp_secret

# ----------------- Main function -----------------
def get_connection(
    api_token: Optional[str] = None,
    api_secret: Optional[str] = None,
    use_env_session_keys: bool = True,
    totp_secret: Optional[str] = None,
    otp: Optional[str] = None,
    save_session: bool = True,
) -> ConnectToIntegrate:
    """
    Returns authenticated ConnectToIntegrate instance.

    Steps:
    1) Try existing session keys from .env (fast path)
    2) If missing/invalid → login via credentials
    3) OTP/TOTP handled automatically if secret provided
    4) Saves session keys to .env
    5) Raises exception if login fails
    """
    dotenv_path = _ensure_dotenv()
    conn = ConnectToIntegrate()

    # 1) Try session keys
    if use_env_session_keys:
        uid = os.getenv("INTEGRATE_UID")
        actid = os.getenv("INTEGRATE_ACTID")
        api_skey = os.getenv("INTEGRATE_API_SESSION_KEY")
        ws_skey = os.getenv("INTEGRATE_WS_SESSION_KEY")
        if uid and actid and api_skey and ws_skey:
            try:
                conn.set_session_keys(uid, actid, api_skey, ws_skey)
                logger.info("Loaded session keys from .env (fast path)")
                return conn
            except Exception as e:
                logger.warning(f"Session keys invalid: {e}")

    # 2) Load credentials if not provided
    if not api_token or not api_secret or not totp_secret:
        creds_token, creds_secret, creds_totp = _get_credentials()
        api_token = api_token or creds_token
        api_secret = api_secret or creds_secret
        totp_secret = totp_secret or creds_totp

    if not api_token or not api_secret:
        logger.error("API credentials missing!")
        raise ValueError("Set INTEGRATE_API_TOKEN / INTEGRATE_API_SECRET in Streamlit secrets or .env")

    # 3) Generate OTP from TOTP if not provided
    if not otp and totp_secret:
        try:
            totp = pyotp.TOTP(totp_secret)
            otp = totp.now()
            logger.debug(f"TOTP generated: {otp}")
        except Exception as e:
            logger.warning(f"TOTP generation failed: {e}")

    # 4) Attempt login
    try:
        logger.info("Attempting login...")
        if otp:
            try:
                conn.login(api_token=api_token, api_secret=api_secret, otp=otp)
            except TypeError:
                conn.login(api_token=api_token, api_secret=api_secret)
        else:
            conn.login(api_token=api_token, api_secret=api_secret)
        logger.info("Login successful!")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

    # 5) Save session keys
    if save_session:
        try:
            uid, actid, api_session_key, ws_session_key = conn.get_session_keys()
            _save_session_keys(dotenv_path, uid, actid, api_session_key, ws_session_key)
        except Exception as e:
            logger.warning(f"Could not save session keys: {e}")

    return conn

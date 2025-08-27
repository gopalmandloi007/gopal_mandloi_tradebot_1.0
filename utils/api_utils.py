# utils/api_utils.py
"""
Centralised connection logic for Definedge Integrate API.
- Reuses session keys from .env to avoid repeated logins.
- Supports OTP (manual) and TOTP (pyotp) generation.
- Saves session keys back to .env after login.
"""

import os
from typing import Optional, Tuple
from integrate import ConnectToIntegrate
from dotenv import load_dotenv, find_dotenv, set_key
import pyotp
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _ensure_dotenv() -> str:
    """
    Ensure there's a .env file in repo root. Returns path to dotenv file.
    """
    path = find_dotenv()
    if not path:
        path = os.path.join(os.getcwd(), ".env")
        # create file if does not exist
        if not os.path.exists(path):
            open(path, "a").close()
    load_dotenv(path)
    return path

def _save_session_keys(dotenv_path: str, uid: str, actid: str, api_session_key: str, ws_session_key: str):
    """
    Save session keys to .env using python-dotenv.set_key
    """
    set_key(dotenv_path, "INTEGRATE_UID", uid)
    set_key(dotenv_path, "INTEGRATE_ACTID", actid)
    set_key(dotenv_path, "INTEGRATE_API_SESSION_KEY", api_session_key)
    set_key(dotenv_path, "INTEGRATE_WS_SESSION_KEY", ws_session_key)
    logger.info("Session keys saved to .env")

def _generate_totp(totp_secret: str) -> str:
    """
    Generate a TOTP code from secret (pyotp)
    """
    totp = pyotp.TOTP(totp_secret)
    return totp.now()

def get_connection(
    api_token: Optional[str] = None,
    api_secret: Optional[str] = None,
    use_env_session_keys: bool = True,
    totp_secret: Optional[str] = None,
    otp: Optional[str] = None,
    save_session: bool = True,
) -> ConnectToIntegrate:
    """
    Returns an authenticated ConnectToIntegrate instance.
    Logic:
      1) Try to load session keys from .env and set them (fast path).
      2) If session keys missing/invalid -> login using api_token/api_secret.
         Optionally use provided otp or totp_secret.
      3) Save session keys to .env if save_session True.
    """
    dotenv_path = _ensure_dotenv()
    conn = ConnectToIntegrate()

    # 1) Try existing session keys
    if use_env_session_keys:
        uid = os.getenv("INTEGRATE_UID")
        actid = os.getenv("INTEGRATE_ACTID")
        api_skey = os.getenv("INTEGRATE_API_SESSION_KEY")
        ws_skey = os.getenv("INTEGRATE_WS_SESSION_KEY")
        if uid and actid and api_skey and ws_skey:
            try:
                conn.set_session_keys(uid, actid, api_skey, ws_skey)
                logger.info("Loaded session keys from .env and set on connection (fast path)")
                return conn
            except Exception as e:
                logger.warning(f"Session keys invalid or setting failed: {e}. Will login.")

    # 2) Need to login
    # find api creds from args or .env
    if not api_token:
        api_token = os.getenv("INTEGRATE_API_TOKEN")
    if not api_secret:
        api_secret = os.getenv("INTEGRATE_API_SECRET")

    if not api_token or not api_secret:
        raise ValueError("API credentials not provided. Set INTEGRATE_API_TOKEN and INTEGRATE_API_SECRET in .env or pass them to get_connection.")

    # compute OTP if totp_secret provided and otp not passed
    if not otp and totp_secret:
        try:
            otp = _generate_totp(totp_secret)
            logger.info("Generated TOTP from provided totp_secret")
        except Exception as e:
            logger.warning(f"Failed to generate TOTP: {e}")

    # Call login (Integrate client example uses api_token/api_secret)
    try:
        # The integrate client in examples used conn.login(api_token=..., api_secret=...)
        # If an otp param is supported, pass it. We'll try both patterns.
        if otp:
            # try passing otp as kwarg - if library doesn't support it will raise; we'll fallback
            try:
                conn.login(api_token=api_token, api_secret=api_secret, otp=otp)
            except TypeError:
                # some versions may expect 'twofa' or no otp param: try without otp
                conn.login(api_token=api_token, api_secret=api_secret)
        else:
            conn.login(api_token=api_token, api_secret=api_secret)
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

    # Save session keys for reuse
    if save_session:
        try:
            uid, actid, api_session_key, ws_session_key = conn.get_session_keys()
            _save_session_keys(dotenv_path, uid, actid, api_session_key, ws_session_key)
        except Exception as e:
            logger.warning(f"Could not fetch/save session keys after login: {e}")

    return conn

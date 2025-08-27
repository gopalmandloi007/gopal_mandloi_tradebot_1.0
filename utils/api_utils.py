"""
Centralized connection logic for Definedge Integrate API.

Behavior:
1. Reuses session keys saved in .env (INTEGRATE_UID, INTEGRATE_ACTID, INTEGRATE_API_SESSION_KEY, INTEGRATE_WS_SESSION_KEY)
2. Loads credentials from:
   - Streamlit secrets (.streamlit/secrets.toml) if running in Streamlit
   - .env file if running locally
3. Supports OTP/TOTP:
   - TOTP secret in secrets.toml or .env
   - Generates OTP automatically if TOTP secret is available
   - Manual OTP can also be provided
4. Saves session keys back to .env after successful login
5. Returns a fully authenticated ConnectToIntegrate object
"""

import os
import logging
from typing import Optional
from integrate import ConnectToIntegrate
import pyotp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------- Internal helpers -------------------
def _ensure_dotenv() -> str:
    """Ensure a .env file exists and load it"""
    from dotenv import load_dotenv, find_dotenv
    path = find_dotenv()
    if not path:
        path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(path):
            open(path, "a").close()
    load_dotenv(path)
    return path

def _save_session_keys(dotenv_path: str, uid: str, actid: str, api_session_key: str, ws_session_key: str):
    """Save session keys to .env"""
    from dotenv import set_key
    set_key(dotenv_path, "INTEGRATE_UID", uid)
    set_key(dotenv_path, "INTEGRATE_ACTID", actid)
    set_key(dotenv_path, "INTEGRATE_API_SESSION_KEY", api_session_key)
    set_key(dotenv_path, "INTEGRATE_WS_SESSION_KEY", ws_session_key)
    logger.info("Session keys saved to .env")

def _get_credentials():
    """
    Returns api_token, api_secret, totp_secret
    Logic:
    - If Streamlit is running, use st.secrets
    - Else fallback to .env
    """
    api_token = api_secret = totp_secret = None

    # Try Streamlit secrets
    try:
        import streamlit as st
        api_token = st.secrets.get("INTEGRATE_API_TOKEN")
        api_secret = st.secrets.get("INTEGRATE_API_SECRET")
        totp_secret = st.secrets.get("totp", {}).get("secret")
    except Exception:
        pass

    # Fallback to .env
    if not api_token or not api_secret:
        from dotenv import load_dotenv
        load_dotenv()
        import os
        api_token = os.getenv("INTEGRATE_API_TOKEN")
        api_secret = os.getenv("INTEGRATE_API_SECRET")
        if not totp_secret:
            totp_secret = os.getenv("TOTP_SECRET")

    return api_token, api_secret, totp_secret

# ------------------- Main function -------------------
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

    Steps:
    1. Try existing session keys from .env (fast path)
       - If running in Streamlit, session keys are used automatically if valid
    2. If session keys missing/invalid → login using api_token/api_secret
       - Auto-generate OTP from TOTP secret if provided
       - Manual OTP supported
    3. Save session keys back to .env for future reuse
    4. Raise exception if login fails (clear error)
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

    # 2) Load credentials if not provided
    if not api_token or not api_secret or not totp_secret:
        creds_token, creds_secret, creds_totp = _get_credentials()
        if not api_token:
            api_token = creds_token
        if not api_secret:
            api_secret = creds_secret
        if not totp_secret:
            totp_secret = creds_totp

    if not api_token or not api_secret:
        raise ValueError(
            "API credentials not provided. Set INTEGRATE_API_TOKEN/SECRET in Streamlit secrets or .env"
        )

    # 3) Generate OTP from TOTP if manual OTP not provided
    if not otp and totp_secret:
        try:
            totp = pyotp.TOTP(totp_secret)
            otp = totp.now()
            logger.info("Generated OTP from TOTP secret")
        except Exception as e:
            logger.warning(f"TOTP generation failed: {e}")

    # 4) Attempt login
    try:
        if otp:
            try:
                conn.login(api_token=api_token, api_secret=api_secret, otp=otp)
            except TypeError:
                # fallback if library does not accept otp param
                conn.login(api_token=api_token, api_secret=api_secret)
        else:
            conn.login(api_token=api_token, api_secret=api_secret)
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

    # 5) Save session keys for future reuse
    if save_session:
        try:
            uid, actid, api_session_key, ws_session_key = conn.get_session_keys()
            _save_session_keys(dotenv_path, uid, actid, api_session_key, ws_session_key)
        except Exception as e:
            logger.warning(f"Could not fetch/save session keys after login: {e}")

    return conn

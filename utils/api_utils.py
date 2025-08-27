import os
import logging
from typing import Optional
from integrate import ConnectToIntegrate
from dotenv import load_dotenv, find_dotenv, set_key

# Optional: only import streamlit if running in Streamlit
try:
    import streamlit as st
    _STREAMLIT_AVAILABLE = True
except ImportError:
    _STREAMLIT_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _ensure_dotenv() -> str:
    path = find_dotenv()
    if not path:
        path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(path):
            open(path, "a").close()
    load_dotenv(path)
    return path

def _save_session_keys(dotenv_path: str, uid: str, actid: str, api_session_key: str, ws_session_key: str):
    from dotenv import set_key
    set_key(dotenv_path, "INTEGRATE_UID", uid)
    set_key(dotenv_path, "INTEGRATE_ACTID", actid)
    set_key(dotenv_path, "INTEGRATE_API_SESSION_KEY", api_session_key)
    set_key(dotenv_path, "INTEGRATE_WS_SESSION_KEY", ws_session_key)
    logger.info("Session keys saved to .env")

def _get_credentials():
    """
    Load credentials from Streamlit secrets if available, else from .env
    """
    api_token = api_secret = totp_secret = None

    if _STREAMLIT_AVAILABLE:
        try:
            api_token = st.secrets.get("INTEGRATE_API_TOKEN")
            api_secret = st.secrets.get("INTEGRATE_API_SECRET")
            totp_secret = st.secrets.get("totp", {}).get("secret")
        except Exception:
            pass

    if not api_token or not api_secret:
        # fallback to .env
        dotenv_path = _ensure_dotenv()
        api_token = os.getenv("INTEGRATE_API_TOKEN")
        api_secret = os.getenv("INTEGRATE_API_SECRET")
        totp_secret = os.getenv("TOTP_SECRET") or totp_secret

    return api_token, api_secret, totp_secret

def get_connection(
    api_token: Optional[str] = None,
    api_secret: Optional[str] = None,
    use_env_session_keys: bool = True,
    totp_secret: Optional[str] = None,
    otp: Optional[str] = None,
    save_session: bool = True,
) -> ConnectToIntegrate:
    from utils.api_utils import _ensure_dotenv, _save_session_keys
    import pyotp

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

    # 2) Load credentials
    if not api_token or not api_secret or not totp_secret:
        api_token, api_secret, totp_secret_env = _get_credentials()
        if totp_secret_env and not totp_secret:
            totp_secret = totp_secret_env

    if not api_token or not api_secret:
        raise ValueError("API credentials not provided. Set INTEGRATE_API_TOKEN/SECRET in Streamlit secrets or .env")

    # 3) Generate OTP if needed
    if not otp and totp_secret:
        try:
            totp = pyotp.TOTP(totp_secret)
            otp = totp.now()
            logger.info("Generated TOTP from secret")
        except Exception as e:
            logger.warning(f"TOTP generation failed: {e}")

    # 4) Login
    try:
        if otp:
            try:
                conn.login(api_token=api_token, api_secret=api_secret, otp=otp)
            except TypeError:
                conn.login(api_token=api_token, api_secret=api_secret)
        else:
            conn.login(api_token=api_token, api_secret=api_secret)
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

    # 5) Save session keys
    if save_session:
        try:
            uid, actid, api_session_key, ws_session_key = conn.get_session_keys()
            _save_session_keys(dotenv_path, uid, actid, api_session_key, ws_session_key)
        except Exception as e:
            logger.warning(f"Could not fetch/save session keys: {e}")

    return conn

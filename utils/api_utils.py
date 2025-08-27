import os
import requests
import pyotp

# Secrets load (streamlit ke secrets.toml se ya env var se)
API_TOKEN = os.getenv("INTEGRATE_API_TOKEN")
API_SECRET = os.getenv("INTEGRATE_API_SECRET")
TOTP_SECRET = os.getenv("TOTP_SECRET")

LOGIN_STEP1_URL = f"https://signin.definedgesecurities.com/auth/realms/debroking/dsbpkc/login/{API_TOKEN}"
LOGIN_STEP2_URL = "https://signin.definedgesecurities.com/auth/realms/debroking/dsbpkc/token"


def login_step1():
    """Step 1 → Send login request to get OTP token"""
    headers = {"api_secret": API_SECRET}
    res = requests.get(LOGIN_STEP1_URL, headers=headers)
    res.raise_for_status()
    return res.json()


def login_step2_manual(otp_token: str, otp: str):
    """Step 2 → Manual OTP entered by user"""
    payload = {"otp_token": otp_token, "otp": otp}
    res = requests.post(LOGIN_STEP2_URL, json=payload)
    res.raise_for_status()
    return res.json()


def login_step2_auto(otp_token: str):
    """Step 2 → Auto OTP generated from TOTP_SECRET"""
    if not TOTP_SECRET:
        raise ValueError("TOTP_SECRET not set")
    
    otp = pyotp.TOTP(TOTP_SECRET).now()
    payload = {"otp_token": otp_token, "otp": otp}
    res = requests.post(LOGIN_STEP2_URL, json=payload)
    res.raise_for_status()
    return {"used_otp": otp, "response": res.json()}

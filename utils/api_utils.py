import os
import requests

BASE_URL = "https://signin.definedgesecurities.com/auth/realms/debroking/dsbpkc"

API_TOKEN = os.getenv("DEFINEDGE_API_TOKEN")
API_SECRET = os.getenv("DEFINEDGE_API_SECRET")

def login_step1():
    """
    Step 1: Send GET request with api_token + api_secret
    Returns otp_token if successful
    """
    url = f"{BASE_URL}/login/{API_TOKEN}"
    headers = {"api_secret": API_SECRET}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()   # contains otp_token


def login_step2(otp_token: str, otp: str):
    """
    Step 2: Send POST request with otp_token + otp
    Returns api_session_key & susertoken
    """
    url = f"{BASE_URL}/token"
    payload = {
        "otp_token": otp_token,
        "otp": otp
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()   # contains api_session_key & susertoken

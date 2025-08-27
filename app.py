import streamlit as st
import os
from api_utils import SessionManager, SessionError

# ----------------------------
# Load secrets
# ----------------------------
def get_secret(key: str, default=None):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

api_token = get_secret("INTEGRATE_API_TOKEN")
api_secret = get_secret("INTEGRATE_API_SECRET")
totp_secret = get_secret("TOTP_SECRET")

# ----------------------------
# UI Setup
# ----------------------------
st.set_page_config(page_title="TradeBot Login", layout="wide")
st.title("🔐 Definedge Login System")

sm = SessionManager(api_token, api_secret, totp_secret)

col1, col2 = st.columns(2)

with col1:
    if st.button("Login with TOTP (auto)"):
        try:
            if sm.login_with_totp():
                st.success("✅ Login Successful with TOTP")
            else:
                st.error("❌ Login Failed with TOTP")
        except SessionError as e:
            st.error(str(e))

with col2:
    if st.button("Step 1: Request OTP"):
        otp_token = sm.request_otp()
        st.session_state["otp_token"] = otp_token
        st.info(f"OTP Token generated: {otp_token}")

    otp_code = st.text_input("Enter OTP")
    if st.button("Step 2: Verify OTP"):
        otp_token = st.session_state.get("otp_token")
        if not otp_token:
            st.warning("Please request OTP first")
        else:
            if sm.verify_otp(otp_token, otp_code):
                st.success("✅ Login Successful with Manual OTP")
            else:
                st.error("❌ OTP Verification Failed")

# ----------------------------
# Status
# ----------------------------
st.divider()
st.subheader("Session Status")
if sm.is_logged_in():
    st.success("✅ Logged in")
    st.json(sm.get_auth_headers())
else:
    st.error("❌ Not logged in")

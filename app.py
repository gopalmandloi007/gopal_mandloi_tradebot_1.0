import streamlit as st
from utils import api_utils

st.title("Definedge Secure Login")

if "otp_token" not in st.session_state:
    st.session_state.otp_token = None
if "api_session_key" not in st.session_state:
    st.session_state.api_session_key = None

# Step 1
if st.button("Send OTP"):
    try:
        res = api_utils.login_step1()
        st.session_state.otp_token = res.get("otp_token")
        st.success(f"OTP sent ✅ (Check mobile/email)")
    except Exception as e:
        st.error(f"Error in Step 1: {e}")

# Step 2
if st.session_state.otp_token:
    otp = st.text_input("Enter OTP", type="password")
    if st.button("Verify OTP"):
        try:
            res = api_utils.login_step2(st.session_state.otp_token, otp)
            st.session_state.api_session_key = res.get("api_session_key")
            st.success(f"Login Successful 🎉\nAPI Session Key: {st.session_state.api_session_key}")
        except Exception as e:
            st.error(f"Error in Step 2: {e}")

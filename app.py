import streamlit as st
from utils.api_utils import login_step1, login_step2_manual, login_step2_auto

st.title("Definedge Login Demo")

if st.button("Step 1: Request OTP Token"):
    try:
        step1_data = login_step1()
        st.session_state["otp_token"] = step1_data.get("otp_token")
        st.success(f"OTP token received: {st.session_state['otp_token']}")
    except Exception as e:
        st.error(f"Error in Step 1: {e}")

if "otp_token" in st.session_state:
    st.subheader("Step 2 Options")

    # Manual OTP
    otp_input = st.text_input("Enter OTP received on mobile/email")
    if st.button("Submit OTP Manually"):
        try:
            data = login_step2_manual(st.session_state["otp_token"], otp_input)
            st.json(data)
        except Exception as e:
            st.error(f"Error in Step 2 Manual: {e}")

    # Auto OTP via TOTP_SECRET
    if st.button("Submit OTP Automatically (TOTP)"):
        try:
            data = login_step2_auto(st.session_state["otp_token"])
            st.write(f"Auto OTP used: {data['used_otp']}")
            st.json(data["response"])
        except Exception as e:
            st.error(f"Error in Step 2 Auto: {e}")

import streamlit as st
from utils.api_utils import get_connection
import os

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("Trading Dashboard - Home")

st.markdown("""
This repo integrates Definedge Integrate API.
Use the left sidebar to navigate pages:
- Portfolio
- Orders
- Orderbook & Tradebook
- Auto Orders (GTT)
- Historical Data
- Scanners, Backtesting, Settings
""")

st.markdown("Ensure API keys in `.streamlit/secrets.toml` or `.env`.")

# ---------------- Sidebar Login ----------------
st.sidebar.header("Login / Session Status")

# Show current status
if 'conn' in st.session_state:
    st.sidebar.success("✅ Already logged in")
else:
    st.sidebar.warning("❌ Not logged in")

# Debug info for secrets
st.sidebar.subheader("Debug Info")
st.sidebar.text(f"INTEGRATE_API_TOKEN: {bool(os.getenv('INTEGRATE_API_TOKEN'))}")
st.sidebar.text(f"INTEGRATE_API_SECRET: {bool(os.getenv('INTEGRATE_API_SECRET'))}")
st.sidebar.text(f"TOTP_SECRET: {bool(os.getenv('TOTP_SECRET'))}")

# Login button
if st.sidebar.button("Login"):
    try:
        st.info("Trying to login...")
        conn = get_connection()
        st.session_state['conn'] = conn
        st.sidebar.success("✅ Login successful!")
        st.success("Login successful!")
    except Exception as e:
        st.sidebar.error(f"❌ Login failed: {e}")
        st.error(f"Error Details: {e}")

# Logout button
if 'conn' in st.session_state:
    if st.sidebar.button("Logout"):
        st.session_state.pop('conn')
        st.sidebar.info("Logged out successfully")

# Main page message
if 'conn' in st.session_state:
    st.info("You are logged in. Access API features now.")
else:
    st.warning("Please login from the sidebar to access API features.")

import streamlit as st
from utils.api_utils import get_connection

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

st.markdown("Make sure you have set API keys in `.streamlit/secrets.toml` or `.env`.")

# ---------------- Sidebar Login ----------------
st.sidebar.header("Login / Session Status")

# Check if already logged in
if 'conn' in st.session_state:
    st.sidebar.success("✅ Already logged in")
else:
    st.sidebar.warning("❌ Not logged in")

# Login button
if st.sidebar.button("Login"):
    try:
        # get_connection() handles credentials from Streamlit secrets or .env
        conn = get_connection()
        st.session_state['conn'] = conn
        st.sidebar.success("✅ Login successful!")
    except Exception as e:
        st.sidebar.error(f"❌ Login failed: {e}")

# Logout button
if 'conn' in st.session_state:
    if st.sidebar.button("Logout"):
        st.session_state.pop('conn')
        st.sidebar.info("Logged out successfully")

# ---------------- Main Page ----------------
if 'conn' in st.session_state:
    st.info("You are logged in. You can now access API features on other pages.")
else:
    st.warning("Please login from the sidebar to access API features.")

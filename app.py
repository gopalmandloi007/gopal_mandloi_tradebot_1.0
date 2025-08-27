import streamlit as st
from utils.api_utils import SessionManager, SessionError

st.set_page_config(page_title="TradeBot", layout="wide")
st.title("💹 Definedge TradeBot")

# ✅ Load credentials from secrets
api_token = st.secrets["INTEGRATE_API_TOKEN"]
api_secret = st.secrets["INTEGRATE_API_SECRET"]
totp_secret = st.secrets.get("TOTP_SECRET")

# ✅ Initialize SessionManager
if "sm" not in st.session_state:
    st.session_state["sm"] = SessionManager(api_token, api_secret, totp_secret)

sm = st.session_state["sm"]

# --- Login Button ---
if st.button("🔑 Login"):
    try:
        resp = sm.login(prefer_totp=True)
        st.success("✅ Logged in successfully")
        st.json(resp)
    except SessionError as e:
        st.error(str(e))

st.divider()
st.subheader("📌 Session Status")
if sm.is_logged_in():
    st.success("Session Active")
    st.json(sm.get_auth_headers())
else:
    st.error("❌ Not logged in")

# --- Example: Holdings API ---
st.divider()
st.subheader("📊 Example API Call (Holdings)")

if sm.is_logged_in():
    if st.button("Get Holdings"):
        try:
            data = sm.call_api("GET", "/integrate/v1/portfolio/holdings")
            st.write("Holdings:")
            st.json(data)
        except SessionError as e:
            st.error(str(e))
else:
    st.warning("⚠️ Please login first.")

# app.py
import streamlit as st

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("Trading Dashboard - Home")

st.markdown("""
This repo integrates Definedge Integrate API.
Use the left sidebar to open pages:
- Portfolio
- Orders
- Orderbook & Tradebook
- Auto Orders (GTT)
- Historical Data
- Scanners, Backtesting, Settings
""")

st.markdown("Make sure you have set API keys in `.streamlit/secrets.toml` or `.env`.")

# pages/2_📈_Orderbook_and_Tradebook.py
import streamlit as st
from utils.order_utils import get_orders, get_gtt_orders
import pandas as pd

st.title("📈 Orderbook & Tradebook")

api_token = st.secrets.get("api", {}).get("token", None)
api_secret = st.secrets.get("api", {}).get("secret", None)

if st.button("Refresh Orders"):
    try:
        orders = get_orders(api_token, api_secret)
        st.subheader("Orders")
        st.dataframe(pd.DataFrame(orders))
    except Exception as e:
        st.error(f"Orders fetch failed: {e}")

if st.button("Refresh GTT Orders"):
    try:
        gtts = get_gtt_orders(api_token, api_secret)
        st.subheader("GTT Orders")
        st.dataframe(pd.DataFrame(gtts))
    except Exception as e:
        st.error(f"GTT fetch failed: {e}")

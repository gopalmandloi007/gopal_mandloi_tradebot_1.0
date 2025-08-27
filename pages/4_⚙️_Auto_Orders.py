# pages/4_⚙️_Auto_Orders.py
import streamlit as st
from utils.order_utils import place_gtt_order, get_gtt_orders
import pandas as pd

st.title("⚙️ Auto Orders (GTT)")

api_token = st.secrets.get("api", {}).get("token", None)
api_secret = st.secrets.get("api", {}).get("secret", None)

symbol = st.text_input("Trading Symbol", "SBIN-EQ")
price = st.number_input("Order Price", value=0.0, format="%.2f")
alert_price = st.number_input("Alert Price", value=0.0, format="%.2f")
qty = st.number_input("Quantity", min_value=1, value=1, step=1)

if st.button("Place GTT Order"):
    try:
        gtt = place_gtt_order(api_token, api_secret, tradingsymbol=symbol, price=float(price), alert_price=float(alert_price), quantity=int(qty))
        st.success("GTT placed")
        st.json(gtt)
    except Exception as e:
        st.error(f"GTT failed: {e}")

if st.button("Refresh GTT Orders"):
    try:
        gtts = get_gtt_orders(api_token, api_secret)
        st.dataframe(pd.DataFrame(gtts))
    except Exception as e:
        st.error(f"Failed: {e}")

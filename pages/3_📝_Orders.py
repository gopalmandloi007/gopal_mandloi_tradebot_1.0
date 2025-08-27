# pages/3_📝_Orders.py
import streamlit as st
from utils.order_utils import place_order, get_orders, get_order_status, get_limits
from utils.api_utils import get_connection
import pandas as pd

st.title("📝 Orders")

api_token = st.secrets.get("api", {}).get("token", None)
api_secret = st.secrets.get("api", {}).get("secret", None)

st.sidebar.header("Credentials (optional)")
st.sidebar.markdown("If not set here, .env will be used.")

symbol = st.text_input("Trading Symbol", "SBIN-EQ")
side = st.selectbox("Side", ["BUY", "SELL"])
quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
order_mode = st.selectbox("Order Mode", ["MARKET", "LIMIT"])
price = st.number_input("Price (for LIMIT)", value=0.0, format="%.2f")

if st.button("Place Order"):
    try:
        ptype = None
        if order_mode == "MARKET":
            ptype = None  # utils will default to MARKET
        else:
            ptype = None  # if integrate needs special PRICE_TYPE_LIMIT, utils will use default - modify if needed
        order = place_order(api_token, api_secret, tradingsymbol=symbol, side=side, price=price, quantity=int(quantity))
        st.success("Order placed")
        st.json(order)
    except Exception as e:
        st.error(f"Order failed: {e}")

if st.button("Refresh Order Book"):
    try:
        orders = get_orders(api_token, api_secret)
        df = pd.DataFrame(orders)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to get orders: {e}")

if st.button("Get Limits/Balance"):
    try:
        lim = get_limits(api_token, api_secret)
        st.json(lim)
    except Exception as e:
        st.error(f"Limits fetch failed: {e}")

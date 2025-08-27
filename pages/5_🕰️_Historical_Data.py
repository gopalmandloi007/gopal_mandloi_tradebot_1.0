# pages/5_🕰️_Historical_Data.py
import streamlit as st
from utils.data_handler import get_historical_data, save_history_to_csv
import pandas as pd
from datetime import datetime, timedelta

st.title("🕰️ Historical Data & Charts")

api_token = st.secrets.get("api", {}).get("token", None)
api_secret = st.secrets.get("api", {}).get("secret", None)

symbol = st.text_input("Symbol", "SBIN-EQ")
today = datetime.today()
start = st.date_input("Start Date", today - timedelta(days=7))
end = st.date_input("End Date", today)

if st.button("Fetch Historical"):
    try:
        data = get_historical_data(api_token, api_secret, symbol=symbol, start=datetime.combine(start, datetime.min.time()), end=datetime.combine(end, datetime.min.time()))
        if not data:
            st.info("No historical data returned.")
        else:
            df = pd.DataFrame(data)
            st.dataframe(df.head(200))
            st.line_chart(df["close"])
            # Save to CSV in data/historical
            out_path = f"data/historical/{symbol.replace('/','_')}_history.csv"
            save_history_to_csv(data, out_path)
            st.success(f"Saved to {out_path}")
    except Exception as e:
        st.error(f"Failed: {e}")

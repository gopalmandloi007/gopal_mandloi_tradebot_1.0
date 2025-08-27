# utils/master_data_loader.py
"""
Simple loader for master symbols CSV (data/master/symbols.csv)
expected columns: trading_symbol, token, segment
"""

import pandas as pd
import os

MASTER_SYMBOLS_PATH = os.path.join("data", "master", "symbols.csv")

def load_master_symbols(path: str = MASTER_SYMBOLS_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        # create empty df template
        df = pd.DataFrame(columns=["trading_symbol", "token", "segment"])
        df.to_csv(path, index=False)
        return df
    return pd.read_csv(path)

def find_token_for_symbol(trading_symbol: str, path: str = MASTER_SYMBOLS_PATH):
    df = load_master_symbols(path)
    row = df[df["trading_symbol"] == trading_symbol]
    if row.empty:
        return None
    return row.iloc[0]["token"]

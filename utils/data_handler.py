# utils/data_handler.py
"""
Data fetch helpers using IntegrateData.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from integrate import IntegrateData
from utils.api_utils import get_connection
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_quote(api_token: Optional[str], api_secret: Optional[str], symbol: str = "SBIN-EQ") -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    ic = IntegrateData(conn)
    return ic.quotes(exchange=conn.EXCHANGE_TYPE_NSE, trading_symbol=symbol)

def get_security_info(api_token: Optional[str], api_secret: Optional[str], symbol: str = "SBIN-EQ") -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    ic = IntegrateData(conn)
    return ic.security_information(exchange=conn.EXCHANGE_TYPE_NSE, trading_symbol=symbol)

def get_historical_data(
    api_token: Optional[str],
    api_secret: Optional[str],
    symbol: str = "SBIN-EQ",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    timeframe: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection(api_token, api_secret)
    ic = IntegrateData(conn)
    if not end:
        end = datetime.today()
    if not start:
        start = end - timedelta(days=1)
    tf = timeframe if timeframe else conn.TIMEFRAME_TYPE_MIN
    history_gen = ic.historical_data(exchange=conn.EXCHANGE_TYPE_NSE, trading_symbol=symbol, timeframe=tf, start=start, end=end)
    return list(history_gen)

def save_history_to_csv(data: List[Dict[str, Any]], filepath: str):
    if not data:
        return
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.info(f"Saved historical to {filepath}")

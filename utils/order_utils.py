# utils/order_utils.py
"""
Order helpers using IntegrateOrders.
"""

from typing import Any, Dict, List, Optional
from integrate import IntegrateOrders
from utils.api_utils import get_connection
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def place_order(
    api_token: Optional[str],
    api_secret: Optional[str],
    tradingsymbol: str,
    side: str = "BUY",          # "BUY" or "SELL"
    price: float = 0.0,
    price_type: str = None,     # use conn.PRICE_TYPE_MARKET or PRICE_TYPE_LIMIT
    product_type: str = None,   # conn.PRODUCT_TYPE_INTRADAY etc.
    quantity: int = 1,
) -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    # default types from conn if not provided
    pt = product_type or conn.PRODUCT_TYPE_INTRADAY
    ptype = price_type or conn.PRICE_TYPE_MARKET
    order_type = conn.ORDER_TYPE_BUY if side.upper() == "BUY" else conn.ORDER_TYPE_SELL

    try:
        order = io.place_order(
            exchange=conn.EXCHANGE_TYPE_NSE,
            order_type=order_type,
            price=price,
            price_type=ptype,
            product_type=pt,
            quantity=quantity,
            tradingsymbol=tradingsymbol,
        )
        logger.info(f"Order placed: {order}")
        return order
    except Exception as e:
        logger.error(f"Place order failed: {e}")
        raise

def place_gtt_order(
    api_token: Optional[str],
    api_secret: Optional[str],
    tradingsymbol: str,
    price: float,
    alert_price: float,
    condition: Optional[str] = None,
    quantity: int = 1,
) -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    cond = condition or conn.GTT_CONDITION_LTP_ABOVE
    try:
        order = io.place_gtt_order(
            exchange=conn.EXCHANGE_TYPE_NSE,
            order_type=conn.ORDER_TYPE_BUY,
            price=price,
            quantity=quantity,
            tradingsymbol=tradingsymbol,
            alert_price=alert_price,
            condition=cond,
        )
        logger.info(f"GTT order placed: {order}")
        return order
    except Exception as e:
        logger.error(f"GTT place failed: {e}")
        raise

def get_orders(api_token: Optional[str], api_secret: Optional[str]) -> List[Dict[str, Any]]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    return io.orders()

def get_gtt_orders(api_token: Optional[str], api_secret: Optional[str]) -> List[Dict[str, Any]]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    return io.gtt_orders()

def get_order_status(api_token: Optional[str], api_secret: Optional[str], order_id: str) -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    return io.order(order_id=order_id)

def cancel_order(api_token: Optional[str], api_secret: Optional[str], order_id: str) -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    return io.cancel(order_id=order_id)

def get_limits(api_token: Optional[str], api_secret: Optional[str]) -> Dict[str, Any]:
    conn = get_connection(api_token, api_secret)
    io = IntegrateOrders(conn)
    return io.limits()

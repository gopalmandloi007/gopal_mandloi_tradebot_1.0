# utils/ws_utils.py
"""
WebSocket helper — support blocking and daemonized connections.
Provide callback hooks or use default logging callbacks.
"""

import logging
from typing import List, Tuple, Callable, Optional
from integrate import IntegrateWebSocket
from utils.api_utils import get_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Type alias for token tuple
Token = Tuple[str, str]

class IntegrateWSManager:
    def __init__(self, conn):
        self.conn = conn
        self.iws = IntegrateWebSocket(conn)
        # default callbacks that simply log
        self.iws.on_login = self._on_login
        self.iws.on_tick_update = self._on_tick
        self.iws.on_order_update = self._on_order
        self.iws.on_depth_update = self._on_depth
        self.iws.on_acknowledgement = self._on_ack
        self.iws.on_exception = self._on_exception
        self.iws.on_close = self._on_close
        self.tokens: List[Token] = []

    def _on_login(self, iws):
        logger.info("WebSocket logged in")

    def _on_tick(self, iws, tick):
        logger.info(f"Tick: {tick}")

    def _on_order(self, iws, order):
        logger.info(f"Order update: {order}")

    def _on_depth(self, iws, depth):
        logger.info(f"Depth: {depth}")

    def _on_ack(self, iws, ack):
        logger.info(f"Ack: {ack}")

    def _on_exception(self, iws, e):
        logger.exception(f"WS exception: {e}")

    def _on_close(self, iws, code, reason):
        logger.info(f"WS closed: {code} {reason}")

    def subscribe_symbols(self, symbols: List[str]):
        """
        symbols: list of trading_symbol strings like "SBIN-EQ" or "TCS-EQ"
        will resolve tokens from conn.symbols and subscribe
        """
        tokens: List[Token] = []
        for s in symbols:
            token = self.get_token_for_symbol(self.conn, self.conn.EXCHANGE_TYPE_NSE, s)
            tokens.append(token)
        self.tokens = tokens

    @staticmethod
    def get_token_for_symbol(conn, exchange: str, trading_symbol: str) -> Token:
        token = next(
            (i["token"] for i in conn.symbols if i["segment"] == exchange and i["trading_symbol"] == trading_symbol),
            None,
        )
        if not token:
            raise Exception(f"Token not found for {trading_symbol}")
        return (exchange, token)

    def connect_blocking(self, ssl_verify: bool = True):
        # subscribe if tokens exist
        if self.tokens:
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_TICK, self.tokens)
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_ORDER, self.tokens)
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_DEPTH, self.tokens)
        self.iws.connect(ssl_verify=ssl_verify)

    def connect_daemon(self, ssl_verify: bool = True):
        if self.tokens:
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_TICK, self.tokens)
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_ORDER, self.tokens)
            self.iws.subscribe(self.conn.SUBSCRIPTION_TYPE_DEPTH, self.tokens)
        self.iws.connect(daemonize=True, ssl_verify=ssl_verify)

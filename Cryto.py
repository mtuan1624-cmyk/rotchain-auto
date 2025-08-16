# crypto.py
from __future__ import annotations
import time
import requests
from typing import Dict, Tuple, List, Optional

COINGECKO = "https://api.coingecko.com/api/v3/simple/price"
BINANCE   = "https://api.binance.com/api/v3/ticker/price"

# Map phổ biến: ticker -> coingecko_id
TICKER_TO_CG = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana",
    "ton": "the-open-network",
}

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "rotchain-auto/1.0"})
    return s

def _with_retry(fn, attempts=2, delay=0.6):
    last_exc = None
    for _ in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    if last_exc:
        # có thể log ra stdout nếu cần
        # print("API error:", last_exc)
        pass
    return None

def normalize_to_cg_ids(symbols: List[str]) -> List[str]:
    ids: List[str] = []
    for s in symbols:
        k = s.strip().lower()
        ids.append(TICKER_TO_CG.get(k, k))  # nếu không map được thì dùng nguyên chuỗi
    return ids

def get_cg_prices(symbols: List[str], vs: str = "usd", timeout: int = 10) -> Dict[str, float]:
    """
    symbols: danh sách id Coingecko (hoặc ticker phổ biến – sẽ auto map)
    """
    ids = ",".join(normalize_to_cg_ids(symbols))
    if not ids:
        return {}

    def _call():
        with _session() as s:
            r = s.get(COINGECKO, params={"ids": ids, "vs_currencies": vs}, timeout=timeout)
            r.raise_for_status()
            return r.json()

    data = _with_retry(_call) or {}
    out: Dict[str, float] = {}
    for k, v in data.items():
        try:
            out[k] = float(v.get(vs, 0.0))
        except Exception:
            out[k] = 0.0
    return out

def get_binance_price(symbol: str = "BTCUSDT", timeout: int = 10) -> Optional[float]:
    def _call():
        with _session() as s:
            r = s.get(BINANCE, params={"symbol": symbol.upper()}, timeout=timeout)
            r.raise_for_status()
            return float(r.json()["price"])
    val = _with_retry(_call)
    return float(val) if val is not None else None

def map_to_binance(symbol: str) -> str:
    # cho phép truyền "btc" hoặc "BTCUSDT"
    s = symbol.upper()
    if s.endswith("USDT"):
        return s
    return f"{s}USDT"

class PriceMemory:
    def __init__(self):
        self.last: Dict[str, float] = {}

    def diff_pct(self, symbol: str, price: float) -> float:
        if price <= 0:
            return 0.0
        old = self.last.get(symbol)
        self.last[symbol] = price
        if not old or old <= 0:
            return 0.0
        return (price - old) / old * 100.0

def check_arbitrage_one(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    symbol: cho phép 'btc','eth','bnb' hoặc coingecko id 'bitcoin','ethereum',...
    Trả về (giá CG(USD), giá Binance(USDT), chênh lệch % nếu đủ dữ liệu)
    """
    # giá Coingecko dùng id
    cg_id = normalize_to_cg_ids([symbol])[0]
    cg_price = get_cg_prices([cg_id], "usd").get(cg_id)

    # giá Binance dùng ticker/USDT
    bn_symbol = map_to_binance(symbol)
    bn_price  = get_binance_price(bn_symbol)

    if cg_price and bn_price:
        diff_pct = (bn_price - cg_price) / cg_price * 100.0
        return (cg_price, bn_price, diff_pct)
    return (cg_price or None, bn_price or None, None)

def format_prices_for_msg(symbols: List[str]) -> str:
    """
    Tiện ích: gộp nhiều giá và chênh lệch thành 1 message HTML.
    """
    lines = ["💹 Giá & chênh lệch:"]
    for sym in symbols:
        cg, bn, df = check_arbitrage_one(sym)
        sym_disp = sym.upper()
        if cg and bn and df is not None:
            lines.append(f"• <b>{sym_disp}</b> CG: <code>{cg:.2f} USD</code> | "
                         f"BN: <code>{bn:.2f} USDT</code> | Δ <b>{df:+.2f}%</b>")
        else:
            lines.append(f"• <b>{sym_disp}</b> dữ liệu chưa đủ.")
    return "\n".join(lines)

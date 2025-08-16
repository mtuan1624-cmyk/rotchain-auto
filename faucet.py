# faucet.py
from __future__ import annotations
import time
import random
from typing import List, Dict, Any, Union, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Header mặc định lịch sự
DEFAULT_HEADERS = {
    "User-Agent": "ROTCHAIN/1.0 (+https://example.com) Python-requests",
    "Accept": "application/json, */*;q=0.8",
}

Endpoint = Union[str, Dict[str, Any]]  # "https://..." hoặc {"url": "...", "method": "POST", ...}

def build_session(proxy: Optional[str] = None, retries: int = 2, backoff: float = 0.5) -> requests.Session:
    """
    Tạo session có retry cơ bản (429/5xx) và mount adapter cho http/https.
    """
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    if proxy:
        s.proxies.update({"http": proxy, "https": proxy})

    return s

def _normalize(ep: Endpoint) -> Dict[str, Any]:
    """
    Chuyển endpoint về dict chuẩn: {url, method, payload, headers, timeout}
    """
    if isinstance(ep, str):
        return {"url": ep, "method": "GET", "payload": None, "headers": {}, "timeout": 15}
    d = dict(ep)  # copy
    d.setdefault("method", "GET")
    d.setdefault("payload", None)
    d.setdefault("headers", {})
    d.setdefault("timeout", 15)
    return d

def probe(session: requests.Session, ep: Endpoint) -> Dict[str, Any]:
    cfg = _normalize(ep)
    url     = cfg["url"]
    method  = str(cfg["method"]).upper()
    payload = cfg.get("payload")
    headers = {**DEFAULT_HEADERS, **(cfg.get("headers") or {})}
    timeout = int(cfg.get("timeout", 15)) or 15

    try:
        if method == "POST":
            r = session.post(url, json=payload or {}, headers=headers, timeout=timeout)
        else:
            r = session.get(url, headers=headers, timeout=timeout)

        status = r.status_code
        ok = 200 <= status < 300
        return {
            "url": url,
            "method": method,
            "status": status,
            "ok": ok,
            "elapsed_ms": int(r.elapsed.total_seconds() * 1000),
        }
    except Exception as e:
        return {"url": url, "method": method, "status": -1, "ok": False, "error": str(e)}

def run_cycle(
    endpoints: List[Endpoint],
    proxy: Optional[str] = None,
    jitter_range: tuple[float, float] = (0.8, 1.6),
) -> List[Dict[str, Any]]:
    """
    Gọi lần lượt danh sách endpoint (GET/POST), có jitter ngẫu nhiên để tránh trùng IP/tần suất.
    """
    if not endpoints:
        return []

    session = build_session(proxy=proxy, retries=2, backoff=0.6)
    results: List[Dict[str, Any]] = []

    for ep in endpoints:
        results.append(probe(session, ep))
        time.sleep(random.uniform(*jitter_range))

    return results

def format_report(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "🚰 Faucet: chưa cấu hình endpoint nào."
    ok = sum(1 for x in results if x.get("ok"))
    total = len(results)
    lines = [f"🚰 Faucet run: OK {ok}/{total} endpoint"]
    for x in results[:10]:
        status = x.get("status")
        ms = x.get("elapsed_ms", 0)
        lines.append(f"• {x['method']} {x['url']} → {status} ({ms} ms)")
    if total > 10:
        lines.append(f"… và {total - 10} endpoint khác.")
    return "\n".join(lines)

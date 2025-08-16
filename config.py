import os
from zoneinfo import ZoneInfo

def getenv_int(key, default=0):
    try:
        return int(os.getenv(key, str(default)).strip())
    except Exception:
        return default

def getenv_list(key):
    raw = os.getenv(key, "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]

class Settings:
    BOT_TOKEN        = os.getenv("BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID = getenv_int("TELEGRAM_CHAT_ID", 0)
    ADMIN_IDS        = set(int(x) for x in getenv_list("ADMIN_IDS"))
    LP_URL           = os.getenv("LP_URL", "https://rotchain.click")

    KEYWORDS = {
        "hi": "Chào bạn 👋",
        "hello": "Hello! 👋",
        "alo": "Mình nghe đây!",
        "ping": "Pong 🏓",
        "giá": "Thông tin giá/ưu đãi xem tại link:"
    }

    CRYPTO_WATCH_ENABLED   = os.getenv("CRYPTO_WATCH_ENABLED", "1") == "1"
    SYMBOLS                = getenv_list("SYMBOLS") or ["btc", "eth", "bnb"]
    ALERT_UP_PCT           = float(os.getenv("ALERT_UP_PCT", "3"))
    ALERT_DOWN_PCT         = float(os.getenv("ALERT_DOWN_PCT", "3"))
    PRICE_BASE_CURRENCY    = os.getenv("PRICE_BASE_CURRENCY", "usd")

    FAUCET_ENABLED         = os.getenv("FAUCET_ENABLED", "0") == "1"
    FAUCET_ENDPOINTS       = getenv_list("FAUCET_ENDPOINTS")
    FAUCET_INTERVAL_MIN    = getenv_int("FAUCET_INTERVAL_MIN", 30)

    DEBUG                  = os.getenv("DEBUG", "0") == "1"
    TZ = ZoneInfo(os.getenv("TZ", "Asia/Ho_Chi_Minh"))

def ensure_core_env():
    if not Settings.BOT_TOKEN or Settings.TELEGRAM_CHAT_ID == 0:
        raise RuntimeError("❌ Thiếu BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong biến môi trường!")

    if Settings.TELEGRAM_CHAT_ID and Settings.TELEGRAM_CHAT_ID not in Settings.ADMIN_IDS:
        Settings.ADMIN_IDS.add(Settings.TELEGRAM_CHAT_ID)

    print(f"[CONFIG] Loaded OK | BOT={bool(Settings.BOT_TOKEN)} | CHAT={Settings.TELEGRAM_CHAT_ID} | TZ={Settings.TZ}")

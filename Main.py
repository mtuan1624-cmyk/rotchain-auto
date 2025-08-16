# main.py
from __future__ import annotations
import asyncio
import logging
from datetime import timedelta
from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters, AIORateLimiter
)

# Local modules
from config import Settings, ensure_core_env
from marketing import Marketing
from crypto import format_prices_for_msg
from faucet import run_cycle, format_report

# ============ Logging ============
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("rotchain")

# ============ Bootstrapping ============
ensure_core_env()
marketing = Marketing(Settings.LP_URL, Settings.KEYWORDS)

# ============ Helpers ============
def is_admin(user_id: int) -> bool:
    return user_id in Settings.ADMIN_IDS

async def safe_reply(update: Update, text: str, **kwargs):
    try:
        await update.effective_chat.send_message(text, **kwargs)
    except Exception as e:
        log.warning("Reply error: %s", e)

# ============ Commands ============
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 Xin chào! Mình là trợ lý dự án ROTCHAIN.\n\n"
        "• /airdrop – Xem danh sách airdrop đang mở\n"
        "• /airdrop_random – Gợi ý 1 airdrop ngẫu nhiên (FOMO)\n"
        "• /prices – Xem giá & chênh lệch (CG vs Binance)\n"
        "• /faucet – Kiểm tra faucet endpoints (admin)\n"
        "• /help – Trợ giúp\n\n"
        f"{marketing.cta()}"
    )
    await safe_reply(update, msg, parse_mode=ParseMode.HTML)

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)

async def cmd_airdrop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    items = marketing.load_airdrops()
    # Có thể lọc theo status/network/limit:
    text = marketing.format_airdrops(items, status="open", network=None, limit=8)
    await safe_reply(update, text, parse_mode=ParseMode.HTML)

async def cmd_airdrop_random(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    items = marketing.load_airdrops()
    text = marketing.random_airdrop(items, status="open", network=None)
    await safe_reply(update, text, parse_mode=ParseMode.HTML)

async def cmd_prices(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # lấy danh sách symbols từ config
    symbols: List[str] = Settings.SYMBOLS
    text = format_prices_for_msg(symbols)
    await safe_reply(update, text, parse_mode=ParseMode.HTML)

async def cmd_faucet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else 0
    if not is_admin(user_id):
        return await safe_reply(update, "⛔ Lệnh này chỉ dành cho admin.")
    if not Settings.FAUCET_ENABLED or not Settings.FAUCET_ENDPOINTS:
        return await safe_reply(update, "Faucet chưa bật hoặc chưa có endpoint.")
    proxy = None  # có thể đọc từ ENV nếu bạn muốn xoay IP
    results = run_cycle(Settings.FAUCET_ENDPOINTS, proxy=proxy)
    await safe_reply(update, format_report(results))

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin broadcast 1 tin nhắn đơn giản vào TELEGRAM_CHAT_ID chính."""
    user_id = update.effective_user.id if update.effective_user else 0
    if not is_admin(user_id):
        return await safe_reply(update, "⛔ Lệnh này chỉ dành cho admin.")
    text = " ".join(ctx.args) if ctx.args else "Thông báo chung từ hệ thống."
    await ctx.bot.send_message(Settings.TELEGRAM_CHAT_ID, text, parse_mode=ParseMode.HTML)
    await safe_reply(update, "✅ Đã gửi.")

async def cmd_ping(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, "pong 🏓")

# ============ Text handler (quick reply) ============
async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    reply = marketing.quick_reply(update.message.text)
    if reply:
        await safe_reply(update, reply, parse_mode=ParseMode.HTML)

# ============ Error handler ============
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error("Update error: %s", context.error)

# ============ Jobs (định kỳ) ============
async def job_prices(context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = format_prices_for_msg(Settings.SYMBOLS)
        await context.bot.send_message(Settings.TELEGRAM_CHAT_ID, msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.warning("job_prices error: %s", e)

async def job_airdrop(context: ContextTypes.DEFAULT_TYPE):
    try:
        items = marketing.load_airdrops()
        msg = marketing.random_airdrop(items, status="open", network=None)
        await context.bot.send_message(Settings.TELEGRAM_CHAT_ID, msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.warning("job_airdrop error: %s", e)

async def job_faucet(context: ContextTypes.DEFAULT_TYPE):
    try:
        if Settings.FAUCET_ENABLED and Settings.FAUCET_ENDPOINTS:
            results = run_cycle(Settings.FAUCET_ENDPOINTS, proxy=None)
            await context.bot.send_message(Settings.TELEGRAM_CHAT_ID, format_report(results))
    except Exception as e:
        log.warning("job_faucet error: %s", e)

# ============ App bootstrap ============
def main():
    application = (
        Application.builder()
        .token(Settings.BOT_TOKEN)
        .rate_limiter(AIORateLimiter(max_retries=2))
        .build()
    )

    # Commands
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("airdrop", cmd_airdrop))
    application.add_handler(CommandHandler("airdrop_random", cmd_airdrop_random))
    application.add_handler(CommandHandler("prices", cmd_prices))
    application.add_handler(CommandHandler("faucet", cmd_faucet))
    application.add_handler(CommandHandler("broadcast", cmd_broadcast))
    application.add_handler(CommandHandler("ping", cmd_ping))

    # Text messages (quick replies)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    # Error hook
    application.add_error_handler(on_error)

    # JobQueue: lịch chạy tự động
    jq = application.job_queue
    # Giá crypto: mỗi 30 phút
    jq.run_repeating(job_prices, interval=timedelta(minutes=30), first=10)
    # Airdrop ngẫu nhiên: mỗi 90 phút
    jq.run_repeating(job_airdrop, interval=timedelta(minutes=90), first=30)
    # Faucet (nếu bật): theo cấu hình phút
    if Settings.FAUCET_ENABLED and Settings.FAUCET_ENDPOINTS:
        jq.run_repeating(job_faucet, interval=timedelta(minutes=max(5, Settings.FAUCET_INTERVAL_MIN)), first=60)

    log.info("Bot starting…")
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

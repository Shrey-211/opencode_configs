#!/usr/bin/env python3
"""
Telegram Bot v2 - Integrated with OpenCode Autonomy System
Production-ready: async I/O, connection pooling, rate limiting, graceful shutdown.
"""

import sys
import time
import asyncio
import logging
from pathlib import Path
from collections import defaultdict
from typing import Optional

import aiohttp
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import config, security_manager

# ---------------------------------------------------------------------------
# Logging (absolute path so it works regardless of cwd)
# ---------------------------------------------------------------------------
LOG_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = LOG_DIR / "telegram_bot_v2.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("telegram_bot_v2")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TELEGRAM_MSG_LIMIT = 4096
CONFIRMATION_TTL_SECONDS = 120
SESSION_IDLE_TTL_SECONDS = 3600
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_MSGS = 30
COMMAND_TIMEOUT = 30
API_MAX_RETRIES = 3
API_RETRY_BACKOFF = 1.5


# ---------------------------------------------------------------------------
# OpenCode HTTP Client (shared singleton, connection-pooled)
# ---------------------------------------------------------------------------
class OpenCodeClient:
    """Async HTTP client for the OpenCode REST API with retry logic."""

    def __init__(self, base_url: str = "http://localhost:4096"):
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=20, keepalive_timeout=30),
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        last_exc: Optional[Exception] = None
        for attempt in range(1, API_MAX_RETRIES + 1):
            try:
                session = await self._get_session()
                async with session.request(method, f"{self.base_url}{path}", **kwargs) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    body = await resp.text()
                    return {"error": f"HTTP {resp.status}: {body[:200]}"}
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_exc = exc
                if attempt < API_MAX_RETRIES:
                    await asyncio.sleep(API_RETRY_BACKOFF * attempt)
                    logger.warning("OpenCode API attempt %d failed: %s", attempt, exc)
        return {"error": f"All {API_MAX_RETRIES} retries failed: {last_exc}"}

    async def create_session(self, title: str = "Telegram Chat") -> dict:
        data = await self._request(
            "POST", "/session",
            json={"title": title, "directory": config.WORKSPACE_PATH},
        )
        if "error" not in data:
            return {"session_id": data.get("id"), "data": data}
        return data

    async def send_prompt(self, session_id: str, text: str) -> dict:
        payload = {
            "parts": [{"type": "text", "text": text}],
            "directory": config.WORKSPACE_PATH,
        }
        data = await self._request("POST", f"/session/{session_id}/message", json=payload)
        if "error" in data:
            return data
        return self._extract_response(data)

    @staticmethod
    def _extract_response(data: dict) -> dict:
        parts = data.get("parts") or data.get("data", {}).get("parts", [])
        text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        full_text = "\n".join(text_parts) or "No response"
        if len(full_text) > TELEGRAM_MSG_LIMIT - 40:
            full_text = full_text[: TELEGRAM_MSG_LIMIT - 40] + "\n\n[Response truncated...]"
        return {"response": full_text}


# ---------------------------------------------------------------------------
# Rate limiter (per-user, sliding window)
# ---------------------------------------------------------------------------
class RateLimiter:
    def __init__(self, window: int = RATE_LIMIT_WINDOW, max_msgs: int = RATE_LIMIT_MAX_MSGS):
        self._window = window
        self._max = max_msgs
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.monotonic()
        timestamps = self._hits[user_id]
        self._hits[user_id] = [t for t in timestamps if now - t < self._window]
        if len(self._hits[user_id]) >= self._max:
            return False
        self._hits[user_id].append(now)
        return True


# ---------------------------------------------------------------------------
# Session / confirmation stores with TTL
# ---------------------------------------------------------------------------
class SessionStore:
    """Tracks OpenCode session IDs per Telegram chat with idle eviction."""

    def __init__(self, idle_ttl: int = SESSION_IDLE_TTL_SECONDS):
        self._idle_ttl = idle_ttl
        self._sessions: dict[str, str] = {}
        self._last_used: dict[str, float] = {}

    def get(self, chat_id: str) -> Optional[str]:
        sid = self._sessions.get(chat_id)
        if sid:
            self._last_used[chat_id] = time.monotonic()
        return sid

    def set(self, chat_id: str, session_id: str):
        self._sessions[chat_id] = session_id
        self._last_used[chat_id] = time.monotonic()

    def remove(self, chat_id: str):
        self._sessions.pop(chat_id, None)
        self._last_used.pop(chat_id, None)

    def purge_stale(self):
        now = time.monotonic()
        stale = [cid for cid, ts in self._last_used.items() if now - ts > self._idle_ttl]
        for cid in stale:
            self.remove(cid)
        if stale:
            logger.info("Purged %d stale sessions", len(stale))


class ConfirmationStore:
    """Stores pending confirmations with automatic TTL expiry."""

    def __init__(self, ttl: int = CONFIRMATION_TTL_SECONDS):
        self._ttl = ttl
        self._pending: dict[str, dict] = {}

    def add(self, confirmation_id: str, data: dict):
        data["created_at"] = time.monotonic()
        self._pending[confirmation_id] = data

    def pop(self, confirmation_id: str) -> Optional[dict]:
        entry = self._pending.pop(confirmation_id, None)
        if entry and time.monotonic() - entry["created_at"] > self._ttl:
            return None
        return entry

    def purge_expired(self):
        now = time.monotonic()
        expired = [k for k, v in self._pending.items() if now - v["created_at"] > self._ttl]
        for k in expired:
            del self._pending[k]
        if expired:
            logger.info("Purged %d expired confirmations", len(expired))


# ---------------------------------------------------------------------------
# Globals (initialized in main)
# ---------------------------------------------------------------------------
opencode_client: OpenCodeClient
sessions: SessionStore
confirmations: ConfirmationStore
rate_limiter: RateLimiter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _truncate(text: str, limit: int = TELEGRAM_MSG_LIMIT - 20) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[truncated]"


def _guard(update: Update) -> bool:
    """Return True if the update has the required message and chat objects."""
    return update.effective_chat is not None and update.message is not None


def _check_access(chat_id: str) -> tuple[bool, Optional[str]]:
    """Check chat-level access (whitelist only, NOT command-level confirmation)."""
    if not config.is_allowed_chat(chat_id):
        return False, "Chat ID not in allowed list"
    return True, None


async def _run_shell(command: str, timeout: int = COMMAND_TIMEOUT) -> dict:
    """Run a shell command asynchronously without blocking the event loop."""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "returncode": proc.returncode,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"returncode": -1, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


# ---------------------------------------------------------------------------
# Periodic housekeeping
# ---------------------------------------------------------------------------
async def _housekeeping_loop():
    """Runs every 60 s to purge stale sessions and expired confirmations."""
    while True:
        await asyncio.sleep(60)
        try:
            sessions.purge_stale()
            confirmations.purge_expired()
        except Exception:
            logger.exception("Housekeeping error")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    allowed, reason = _check_access(chat_id)
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    welcome = (
        "**OpenCode Autonomy Bot v2**\n\n"
        "Quick Start:\n"
        "/run <command> - Run shell commands\n"
        "/sysinfo - Check system status\n"
        "/newchat - Start new AI chat session\n"
        "/help - Show all commands\n\n"
        "Just send a message to chat with AI."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    help_text = (
        "**OpenCode Autonomy Bot v2**\n\n"
        "**System Control:**\n"
        "/run <command> - Shell command\n"
        "/sysinfo - CPU, RAM, Disk\n"
        "/volume <0-100> - Set volume\n"
        "/brightness <0-100> - Set brightness\n\n"
        "**Chat:**\n"
        "/newchat - New AI session\n"
        "/clearchat - Clear session\n\n"
        "Send any message to chat with AI."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def newchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    sessions.remove(chat_id)
    await update.message.reply_text("Session cleared. Send a message to start a new chat.")


async def clearchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    sessions.remove(chat_id)
    await update.message.reply_text("Chat cleared.")


# ---------------------------------------------------------------------------
# /run
# ---------------------------------------------------------------------------
async def run_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    allowed, reason = _check_access(chat_id)
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return

    command = " ".join(context.args)

    if security_manager.requires_confirmation(command):
        await _request_confirmation(update, command, "run")
        return

    await _execute_run(update, command, chat_id)


async def _execute_run(update: Update, command: str, chat_id: str):
    status_msg = await update.message.reply_text(f"Running: `{command}`", parse_mode="Markdown")
    r = await _run_shell(command)
    output = r["stdout"] or r["stderr"] or "Command executed (no output)"
    output = _truncate(output, TELEGRAM_MSG_LIMIT - 30)

    try:
        await status_msg.edit_text(f"```\n{output}\n```", parse_mode="Markdown")
    except Exception:
        await status_msg.edit_text(output[:TELEGRAM_MSG_LIMIT])

    security_manager.audit_log(chat_id, command, r["returncode"] == 0, "Command executed")


# ---------------------------------------------------------------------------
# /sysinfo
# ---------------------------------------------------------------------------
async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    allowed, reason = _check_access(chat_id)
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    try:
        cpu = await asyncio.to_thread(psutil.cpu_percent, interval=1)
        mem = await asyncio.to_thread(psutil.virtual_memory)
        disk = await asyncio.to_thread(psutil.disk_usage, "/")

        text = (
            f"**System Information**\n\n"
            f"**CPU:** {cpu}%\n"
            f"**Memory:** {mem.percent}% ({mem.available / (1024**3):.1f} GB free)\n"
            f"**Disk:** {disk.percent}% ({disk.free / (1024**3):.1f} GB free)\n"
            f"**Python:** {sys.version.split()[0]}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.exception("sysinfo failed")
        await update.message.reply_text(f"Error: {e}")


# ---------------------------------------------------------------------------
# Confirmation flow
# ---------------------------------------------------------------------------
async def _request_confirmation(update: Update, command: str, command_type: str):
    confirmation_id = f"{update.effective_chat.id}_{command_type}_{time.monotonic():.4f}"
    confirmations.add(confirmation_id, {
        "chat_id": str(update.effective_chat.id),
        "command": command,
        "type": command_type,
    })

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Confirm", callback_data=f"cfm:{confirmation_id}"),
            InlineKeyboardButton("Cancel", callback_data=f"cxl:{confirmation_id}"),
        ]
    ])
    await update.message.reply_text(
        f"**Confirmation Required**\n\nCommand: `{command}`\n\nProceed?",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    data = query.data or ""
    if ":" not in data:
        await query.edit_message_text("Invalid callback.")
        return

    action, confirmation_id = data.split(":", 1)
    pending = confirmations.pop(confirmation_id)

    if pending is None:
        await query.edit_message_text("Confirmation expired or invalid.")
        return

    if action == "cxl":
        await query.edit_message_text("Command cancelled.")
        return

    if action == "cfm":
        await query.edit_message_text("Confirmed. Executing...")
        chat_id = pending["chat_id"]
        command = pending["command"]
        cmd_type = pending["type"]

        if cmd_type == "run":
            await _execute_run(update, command, chat_id)


# ---------------------------------------------------------------------------
# AI chat (free-form messages)
# ---------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _guard(update):
        return
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    if not text:
        return

    allowed, reason = _check_access(chat_id)
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    if not rate_limiter.is_allowed(chat_id):
        await update.message.reply_text("Rate limit reached. Please wait a moment.")
        return

    try:
        session_id = sessions.get(chat_id)
        if session_id is None:
            result = await opencode_client.create_session(title=f"Telegram User {chat_id}")
            if "error" in result:
                await update.message.reply_text(f"Failed to create session: {result['error']}")
                return
            session_id = result["session_id"]
            sessions.set(chat_id, session_id)

        thinking_msg = await update.message.reply_text("Thinking...")
        result = await opencode_client.send_prompt(session_id, text)

        if "error" in result:
            await thinking_msg.edit_text(f"Error: {result['error']}")
        else:
            response = result.get("response", "No response")
            await thinking_msg.edit_text(response)
    except Exception as e:
        logger.exception("Message handling failed")
        await update.message.reply_text(f"Error: {e}")


# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("An internal error occurred. Please try again.")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------
async def post_init(app: Application):
    """Called after the Application is initialized."""
    global opencode_client, sessions, confirmations, rate_limiter
    opencode_client = OpenCodeClient()
    sessions = SessionStore()
    confirmations = ConfirmationStore()
    rate_limiter = RateLimiter()
    asyncio.create_task(_housekeeping_loop())
    logger.info("Bot initialized — housekeeping task started")


async def post_shutdown(app: Application):
    """Called during graceful shutdown."""
    await opencode_client.close()
    logger.info("Bot shut down — resources cleaned up")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    errors = config.validate()
    if errors:
        for e in errors:
            logger.error("Config error: %s", e)
        sys.exit(1)

    app = (
        Application.builder()
        .token(config.TELEGRAM_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("newchat", newchat_command))
    app.add_handler(CommandHandler("clearchat", clearchat_command))
    app.add_handler(CommandHandler("run", run_command_handler))
    app.add_handler(CommandHandler("sysinfo", sysinfo_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("OpenCode Autonomy Bot v2 starting...")
    logger.info("Allowed chats: %s", "All" if not config.ALLOWED_CHAT_IDS else config.ALLOWED_CHAT_IDS)

    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

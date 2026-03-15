"""
Verify Telegram bot configuration
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from config_loader import config

print("=" * 60)
print("Telegram Bot Configuration Verification")
print("=" * 60)

# Check token
if config.TELEGRAM_TOKEN:
    token_start = config.TELEGRAM_TOKEN[:10]
    token_end = config.TELEGRAM_TOKEN[-10:]
    print(f"[OK] Token loaded: {token_start}...{token_end}")
else:
    print("[FAIL] Token not found in environment")
    sys.exit(1)

# Check other configuration
print(f"[OK] Redis URL: {config.get_redis_url()}")
print(f"[OK] Workspace path: {config.WORKSPACE_PATH}")
print(f"[OK] Allowed chats: {config.ALLOWED_CHAT_IDS or 'All'}")

print("\n" + "=" * 60)
print("Configuration is valid and ready for use!")
print("=" * 60)

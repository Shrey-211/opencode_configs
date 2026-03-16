# Setup Guide

## Prerequisites

- Python 3.10+
- OpenCode installed and on PATH
- Telegram Bot token (from [@BotFather](https://t.me/BotFather))

## Step 1: Configure Environment

Copy the template and fill in your token:

```bash
copy example.env .env
```

Edit `.env`:

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Optional: restrict to specific Telegram chat IDs (comma-separated)
# ALLOWED_CHAT_IDS=123456789,987654321
```

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Start OpenCode Server

```bash
opencode serve
```

Verify it's running:

```bash
curl http://localhost:4096/global/health
```

## Step 4: Start Telegram Bot

**Option A** -- Use the restart script (recommended, runs in background):

```bash
powershell -ExecutionPolicy Bypass -File restart_bot.ps1
```

**Option B** -- Run directly (foreground, useful for debugging):

```bash
python tools/telegram_bot_v2.py
```

## Step 5: Test

Open Telegram, find `@Open_codebot`, and send `/start`.

## Configuration Reference

All config lives in `.env`. See `example.env` for the full list.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_TOKEN` | Yes | -- | Bot token from @BotFather |
| `ALLOWED_CHAT_IDS` | No | *(empty = all)* | Comma-separated chat ID whitelist |
| `WORKSPACE_PATH` | No | `D:/workspace/open_code` | Default working directory |
| `REQUIRE_CONFIRMATION` | No | `true` | Require confirmation for dangerous commands |
| `DANGEROUS_COMMANDS` | No | `shutdown,restart,kill,rm,format,mkfs` | Keywords that trigger confirmation |

## Troubleshooting

### "OpenCode server not running"

Start the server first:

```bash
opencode serve
curl http://localhost:4096/global/health
```

### Telegram 409 conflict error

Another bot instance is running. Kill all Python processes and restart:

```bash
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
powershell -ExecutionPolicy Bypass -File restart_bot.ps1
```

### Bot not responding

Check the log:

```bash
type C:\Users\Shrey\.config\opencode\telegram_bot_v2.log
```

### Permission denied on commands

Verify your Telegram chat ID is in `ALLOWED_CHAT_IDS` (or leave it empty to allow all).

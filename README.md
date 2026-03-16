# OpenCode Remote Control

> **Author**: Shreyas Jadhav (SDET, Pune, India)
> **Repository**: [Shrey-211/opencode_configs](https://github.com/Shrey-211/opencode_configs)

A production-ready Telegram bot that gives you remote control of your PC and AI chat powered by OpenCode.

## What It Does

- **AI Chat** -- Send any message to chat with OpenCode AI via Telegram (persistent sessions per user)
- **Remote Shell** -- Run shell commands on your PC from anywhere (`/run`)
- **System Info** -- Check CPU, RAM, disk from your phone (`/sysinfo`)
- **Voice** -- Text-to-speech and speech-to-text tools
- **Browser Automation** -- Control Chrome via Selenium

## Quick Start

```bash
# 1. Configure
copy example.env .env   # then edit with your TELEGRAM_TOKEN

# 2. Install
pip install -r requirements.txt

# 3. Start OpenCode server
opencode serve

# 4. Start bot
powershell -ExecutionPolicy Bypass -File restart_bot.ps1

# 5. Open Telegram and message @Open_codebot
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| *(any message)* | Chat with OpenCode AI |
| `/newchat` | Start a new AI session |
| `/clearchat` | Clear current session |
| `/run <cmd>` | Run a shell command (async, 30s timeout) |
| `/sysinfo` | CPU, RAM, disk usage |
| `/help` | Show all commands |

## Production Features

The Telegram bot (`tools/telegram_bot_v2.py`) is built for reliability:

- **Connection-pooled HTTP client** -- Shared singleton `OpenCodeClient` with `TCPConnector`
- **Retry with backoff** -- 3 retries with exponential backoff on API failures
- **Rate limiting** -- Per-user sliding window (30 msgs / 60s)
- **Session management** -- Idle eviction after 1 hour, background cleanup every 60s
- **Confirmation flow** -- Dangerous commands require inline button confirmation (120s TTL)
- **Fully async** -- `asyncio.create_subprocess_shell`, `asyncio.to_thread` for blocking calls
- **Graceful lifecycle** -- `post_init` / `post_shutdown` hooks for resource management
- **Global error handler** -- Uncaught exceptions logged, user notified
- **Drop pending updates** -- Skips stale message backlog on restart

## Project Structure

```
C:\Users\Shrey\.config\opencode\
├── utils/                   # Shared utilities
│   ├── config_loader.py     # .env loading and validation
│   ├── security.py          # Whitelist, confirmation, audit log
│   └── task_queue.py        # Arq + Redis task queue
├── tools/                   # Bot and automation tools
│   ├── telegram_bot_v2.py   # Production Telegram bot
│   ├── speak.py             # Text-to-speech (Windows Speech Synthesis)
│   ├── listen.py            # Speech-to-text (Google Speech API)
│   ├── selenium_tool.py     # Chrome browser automation
│   └── spotify.py           # Spotify integration
├── docs/                    # Documentation
│   ├── CAPABILITIES.md      # Full capabilities guide
│   ├── SETUP_GUIDE.md       # Installation walkthrough
│   └── FILE_STRUCTURE.md    # File structure reference
├── .env                     # Secrets (not in git)
├── example.env              # Template
├── opencode.json            # OpenCode MCP + skills config
├── restart_bot.ps1          # Bot restart script
├── AGENTS.md                # Agent instructions
└── requirements.txt         # Python dependencies
```

## Security

- **Chat ID whitelist** -- `ALLOWED_CHAT_IDS` in `.env` (empty = allow all)
- **Dangerous command confirmation** -- `shutdown`, `kill`, `rm`, etc. require inline button confirm
- **Audit logging** -- All commands logged to `audit_log.txt`
- **Secrets in `.env`** -- Never committed to git

## Docs

- [Setup Guide](docs/SETUP_GUIDE.md) -- Step-by-step installation
- [Capabilities](docs/CAPABILITIES.md) -- Full tool and feature reference
- [File Structure](docs/FILE_STRUCTURE.md) -- Codebase layout

## License

MIT

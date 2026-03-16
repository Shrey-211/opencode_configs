# File Structure

```
C:\Users\Shrey\.config\opencode\
│
├── utils/                       # Shared utility modules
│   ├── __init__.py              # Exports config, security_manager, task_queue
│   ├── config_loader.py         # Loads .env, validates config, exposes Config class
│   ├── security.py              # Chat whitelist, confirmation, audit logging
│   └── task_queue.py            # Arq + Redis background task queue
│
├── tools/                       # Bot and automation tools
│   ├── telegram_bot_v2.py       # Production Telegram bot (main entry point)
│   ├── speak.py                 # Text-to-speech (Windows Speech Synthesis)
│   ├── speak.json               # Speak tool MCP config
│   ├── speak.js                 # Speak tool JS wrapper
│   ├── listen.py                # Speech-to-text (Google Speech API)
│   ├── listen.json              # Listen tool MCP config
│   ├── selenium_tool.py         # Chrome browser automation (Selenium)
│   └── spotify.py               # Spotify integration
│
├── docs/                        # Documentation
│   ├── CAPABILITIES.md          # Full tool and feature reference
│   ├── SETUP_GUIDE.md           # Installation walkthrough
│   └── FILE_STRUCTURE.md        # This file
│
├── .env                         # Environment variables (NOT in git)
├── example.env                  # .env template for new setups
├── .gitignore                   # Git exclusions
├── opencode.json                # OpenCode MCP servers + skills config
├── package.json                 # Node.js dependencies
├── requirements.txt             # Python dependencies
├── restart_bot.ps1              # PowerShell script to restart the bot
├── AGENTS.md                    # Agent instructions (auto-loaded by OpenCode)
├── README.md                    # Project overview
└── telegram_bot_v2.log          # Bot runtime log (auto-created)
```

## Package Dependencies

```
utils → (standalone, no internal deps)
tools/telegram_bot_v2.py → utils (config, security_manager)
```

## Running

1. Start OpenCode server: `opencode serve`
2. Start Telegram bot: `powershell -ExecutionPolicy Bypass -File restart_bot.ps1`

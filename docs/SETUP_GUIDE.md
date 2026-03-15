# Setup Guide - OpenCode Autonomy System v2

## Prerequisites

1. **Python 3.8+**
2. **Redis Server** (for task queue)
3. **OpenCode** installed and configured
4. **Telegram Bot Token** (from @BotFather)

## Quick Start

### Step 1: Configure Environment

1. Copy `example.env` to `.env`:
   ```bash
   copy example.env .env
   ```

2. Edit `.env` with your values:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start Redis

```bash
# Windows (if installed via Chocolatey)
redis-server

# Or download from: https://github.com/tporadowski/redis/releases
```

### Step 4: Start OpenCode Server

```bash
opencode serve
```

Verify it's running:
```bash
curl http://localhost:4096/global/health
```

### Step 5: Start Telegram Bot

```bash
python tools/telegram_bot_v2.py
```

### Step 6: Test the System

```bash
python utils/test_integration.py
```

## Configuration Details

### Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create a bot
4. Copy the token provided

### AI API Keys (Optional)

- **Google Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys

### Redis Configuration

Default settings work for local development:
- Host: `localhost`
- Port: `6379`
- Database: `0`

## File Structure Overview

```
opencode/
├── utils/           # Configuration, security, task queue
├── agents/          # Multi-agent system
├── multiagent/      # Agent coordination
├── nlp/             # Natural language processing
├── monitoring/      # System monitoring
├── tools/           # Telegram bot and tools
├── docs/            # Documentation
└── .env             # Your configuration (NOT in git)
```

## Common Issues

### "Redis connection failed"
- Ensure Redis is running: `redis-cli ping`
- Check `REDIS_HOST` and `REDIS_PORT` in `.env`

### "OpenCode server not running"
- Start with: `opencode serve`
- Verify with: `curl http://localhost:4096/global/health`

### "Bot not responding"
- Check token in `.env`
- Ensure bot is running in background
- Check `telegram_bot_v2.log` for errors

## Next Steps

1. Read `docs/README_AUTONOMY.md` for comprehensive documentation
2. Try commands in Telegram:
   - `/start` - Welcome message
   - `/help` - Command list
   - `/goal Open browser and search for Python` - Test goal execution
3. Review `docs/FILE_STRUCTURE.md` for organization details

## Security Notes

- Never commit `.env` file to version control
- Use environment variables for all secrets
- Enable command confirmation for dangerous operations
- Restrict bot access with `ALLOWED_CHAT_IDS`

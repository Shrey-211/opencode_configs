# OpenCode Remote Control -- Capabilities Guide

> **Author**: Shreyas Jadhav (SDET, Pune, India)
> **Repository**: [Shrey-211/opencode_configs](https://github.com/Shrey-211/opencode_configs)

---

## Telegram Bot (`telegram_bot_v2.py`)

**Bot**: `@Open_codebot`
**Requires**: OpenCode server on `localhost:4096`

### AI Chat
Send any message to get a response from OpenCode AI. Sessions are persistent per user and automatically evicted after 1 hour of inactivity.

| Command | Description |
|---------|-------------|
| *(any text)* | Chat with AI |
| `/newchat` | Start fresh session |
| `/clearchat` | Clear current session |

### System Control

| Command | Description |
|---------|-------------|
| `/run <command>` | Async shell execution (30s timeout) |
| `/sysinfo` | CPU, RAM, disk usage |

### Security

| Feature | Details |
|---------|---------|
| Chat whitelist | `ALLOWED_CHAT_IDS` in `.env` (empty = allow all) |
| Dangerous command confirmation | Inline buttons, 120s expiry |
| Audit logging | All commands written to `audit_log.txt` |
| Rate limiting | 30 messages per 60 seconds per user |

### Production Internals

| Feature | Implementation |
|---------|---------------|
| HTTP client | Shared `aiohttp.ClientSession` with `TCPConnector(limit=20)` |
| API retries | 3 attempts, exponential backoff (1.5x) |
| Session store | In-memory dict with 1-hour idle TTL |
| Confirmation store | In-memory dict with 120s TTL |
| Housekeeping | Background `asyncio.Task` runs every 60s |
| Subprocess | `asyncio.create_subprocess_shell` (non-blocking) |
| Blocking calls | `asyncio.to_thread` for `psutil` |
| Lifecycle | `post_init` / `post_shutdown` hooks |
| Error handler | Global handler logs + notifies user |

---

## Text-to-Speech (`speak.py`)

**Technology**: Windows Speech Synthesis via PowerShell
**Execution**: Background (`Popen`) -- non-blocking

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | *(required)* | Text to speak |
| `voice` | `en-US-AriaNeural` | Voice selection |
| `rate` | `0` | Speech rate adjustment |
| `volume` | `100` | Volume (0-100) |

**Available voices**: Microsoft David Desktop, Hazel Desktop, Zira Desktop

---

## Speech-to-Text (`listen.py`)

**Technology**: `speech_recognition` library + Google Speech API

| Parameter | Default | Description |
|-----------|---------|-------------|
| `timeout` | `10` | Listening timeout (seconds) |
| `phrase_limit` | `5` | Max phrase duration (seconds) |
| `language` | `en-US` | Recognition language |

---

## Browser Automation (`selenium_tool.py`)

**Technology**: Selenium + Chrome WebDriver
**Requires**: `pip install selenium webdriver-manager`

Persistent Chrome instance with commands:

| Action | Description |
|--------|-------------|
| Open/navigate | Load a URL |
| Click | CSS selector targeting |
| Type | Fill input fields |
| Get text | Extract element content |
| Screenshot | Capture current page |
| Close | Terminate browser |

---

## Spotify Integration (`spotify.py`)

Search and play tracks via Spotify.

---

## OpenCode MCP Integrations (`opencode.json`)

| MCP Server | Purpose |
|------------|---------|
| Playwright | Browser automation |
| Filesystem | File operations (scoped paths) |
| Memory | Persistent knowledge graph |
| GitHub | Repository management |
| Context7 | Documentation lookup |

---

## Configuration (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | Yes | Bot token from @BotFather |
| `ALLOWED_CHAT_IDS` | No | Comma-separated whitelist (empty = all) |
| `WORKSPACE_PATH` | No | Default working directory |
| `REQUIRE_CONFIRMATION` | No | Enable dangerous command confirmation (default: true) |
| `DANGEROUS_COMMANDS` | No | Comma-separated keywords (default: shutdown,restart,kill,rm,format,mkfs) |

See `example.env` for the full template.

---

*Last Updated: March 17, 2026*

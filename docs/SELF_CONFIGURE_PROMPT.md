# Self-Configuration Prompt for OpenCode

Give this prompt to a freshly installed OpenCode instance. It will clone the repo, install everything, and configure itself. The user only needs to provide their API tokens when asked.

## Prerequisites (must be installed before running the prompt)

- [OpenCode](https://opencode.ai) installed and on PATH
- Node.js 18+ and npm
- Python 3.10+
- Git
- Chrome browser (optional, for Selenium automation)
- A Telegram bot token from [@BotFather](https://t.me/BotFather) (optional, for remote control)

---

## The Prompt

Copy everything below the line and paste it as your first message to OpenCode:

---

```
I want you to configure this OpenCode installation as a remote-control AI assistant with a Telegram bot, voice tools, browser automation, and MCP integrations. Follow these steps precisely:

## Step 1: Clone the config repo

Clone https://github.com/Shrey-211/opencode_configs into the OpenCode config directory. The config directory is at: ~/.config/opencode/ (or %USERPROFILE%\.config\opencode\ on Windows).

If files already exist in that directory, back them up first:
- If opencode.json exists, rename it to opencode.json.backup
- If AGENTS.md exists, rename it to AGENTS.md.backup

Then clone the repo contents directly into the config directory (not as a subdirectory):
  git clone https://github.com/Shrey-211/opencode_configs.git temp_clone
  # Copy all files from temp_clone/ into the config directory
  # Remove temp_clone/

## Step 2: Fix user-specific paths

The repo has hardcoded paths for the original author. Replace them with my actual paths:

1. In opencode.json, find the filesystem MCP server entry and replace the paths:
   - Replace "D:/workspace" with my actual workspace/projects directory
   - Replace "C:/Users/Shrey" with my actual home directory (resolve ~ or %USERPROFILE%)

2. In example.env:
   - Replace WORKSPACE_PATH value with my projects directory
   - Replace SCREENSHOT_DIR value with a screenshots folder inside my projects directory

3. In AGENTS.md:
   - Replace all occurrences of "C:\Users\Shrey" or "C:/Users/Shrey" with my home directory
   - Replace all occurrences of "D:/workspace/open_code" with my projects directory

4. In restart_bot.ps1:
   - Replace the Python path with the actual python.exe location (run: where python or which python)
   - Replace all occurrences of "C:\Users\Shrey\.config\opencode" with the actual config directory path

## Step 3: Install dependencies

Run these commands in the config directory:
  npm install
  pip install python-dotenv aiohttp psutil python-telegram-bot

Optional (for full feature set):
  pip install SpeechRecognition selenium webdriver-manager spotipy

## Step 4: Create .env file

Copy example.env to .env, then ask me for these values one at a time:
  - TELEGRAM_TOKEN (required for the Telegram bot - get from @BotFather on Telegram)
  - GITHUB_TOKEN (optional - for GitHub MCP integration)
  - SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET (optional - for Spotify control)

For any token I say "skip", leave the placeholder value.

## Step 5: Clean up dead code

Delete these directories and files if they exist (they are remnants of an old multi-agent system that was removed):
  - agents/ directory
  - multiagent/ directory
  - nlp/ directory
  - monitoring/ directory
  - memory/ directory
  - utils/test_integration.py
  - utils/verify_bot.py
  - utils/task_queue.py
  - docs/README_AUTONOMY.md
  - docs/IMPLEMENTATION_SUMMARY.md

Also remove the task_queue import from utils/__init__.py (keep only config and security_manager).

## Step 6: Verify the setup

1. Check that opencode.json is valid JSON and all MCP server commands are correct
2. Check that .env has TELEGRAM_TOKEN set (if I provided one)
3. Run: python -c "from utils import config; print('Config OK:', config.validate())"
4. Run: curl http://localhost:4096/global/health (to check if OpenCode server is running)

## Step 7: Start services (if Telegram token was provided)

1. Start the Telegram bot:
   - On Windows: powershell -ExecutionPolicy Bypass -File restart_bot.ps1
   - On Linux/Mac: nohup python tools/telegram_bot_v2.py &

2. Tell me the bot is ready and I can message @Open_codebot on Telegram.

## What this gives me

After setup, I'll have:
- 6 MCP servers: Playwright (browser), Filesystem, Memory (knowledge graph), GitHub, Scrapling (web scraping), Context7 (docs)
- 5 skills: find-skills, web-design-guidelines, vercel-react-best-practices, typescript-best-practices, bug-fix
- Custom tools: text-to-speech (speak), speech-to-text (listen), Windows system control, Chrome automation (Selenium)
- A production Telegram bot with: AI chat, remote shell execution, system info, rate limiting, confirmation for dangerous commands, retry logic, and graceful shutdown
- AGENTS.md with instructions for how I want the AI to behave

Ask me for my OS, home directory path, and workspace path before starting. Then proceed step by step, showing me what you're doing at each stage.
```

---

## What the Prompt Does NOT Handle

These require manual action by the user outside of OpenCode:

1. **Installing prerequisites** -- Node.js, Python, Chrome, Git, OpenCode itself
2. **Creating the Telegram bot** -- User must talk to @BotFather on Telegram to get a token
3. **Spotify OAuth** -- Requires browser login flow after setup
4. **GitHub token** -- User must create a personal access token at github.com/settings/tokens
5. **Microphone access** -- The listen tool needs a working microphone and `SpeechRecognition` library
6. **Windows-only tools** -- speak.py and windows.py use PowerShell; they won't work on Linux/Mac without replacement implementations

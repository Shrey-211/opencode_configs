# OpenCode Agent Instructions

Add your custom rules and instructions below. These will be automatically loaded when opencode runs in this project.

## Examples

- Always use memory tools (memory_create_entities, memory_add_observations) to store persistent information about the user and their preferences
- Always create memory entries for user facts (name, preferences, project details, actions taken)
- Always refer to opencode.json for MCP and tool configurations available in this project
- Remember user's coding preferences, project details, and any important actions they take
- Store relevant context in memory at the start of each session and update it as needed
- Automatically create and store a summary of the conversation in memory every 15-20 messages or at end of session using memory_add_observations
- At the start of each session: read memory, find message_counter, increment it after each user message
- When message_counter reaches 15, create a session summary and reset counter to 0
- Use the speak tool to voice important responses or summaries when appropriate
- Include key decisions, code changes, and important information in the session summary
- Use specific coding conventions
- Default test framework to use
- Preferred libraries or patterns

## Speak Tool Configuration

- **Tool location**: C:/Users/Shrey/.config/opencode/tools/speak.py
- **Config location**: C:/Users/Shrey/.config/opencode/tools/speak.json
- **Technology**: Windows Speech Synthesis (System.Speech) via PowerShell
- **Optimization**: Uses Popen for background execution - no waiting, instant return
- **Available voices**: Microsoft David Desktop, Microsoft Hazel Desktop, Microsoft Zira Desktop
- **Usage**: Use speak tool for all verbal responses to user (audio-first communication)
- **Parameters**: text (required), voice (default: en-US-AriaNeural), rate, volume
- **Speed note**: Speech runs asynchronously - no delay after speaking

## Listen Tool Configuration (Speech-to-Text)

- **Tool location**: C:/Users/Shrey/.config/opencode/tools/listen.py
- **Config location**: C:/Users/Shrey/.config/opencode/tools/listen.json
- **Technology**: speech_recognition library with Google Speech API
- **Usage**: Use to listen to user's speech and convert to text
- **Parameters**: timeout (default 10s), phrase_limit (default 5s), language (default en-US)
- **Library**: pip install SpeechRecognition

## Telegram Bot (Remote Control + OpenCode AI)

- **Bot username**: @Open_codebot
- **Token**: Set via TELEGRAM_TOKEN environment variable in .env
- **Tool location**: C:/Users/Shrey/.config/opencode/tools/telegram_bot.py
- **Run**: python C:/Users/Shrey/.config/opencode/tools/telegram_bot.py
- **Requires**: OpenCode server running on localhost:4096
- **Integration**: Uses OpenCode REST API for AI chat

### AI Chat Commands
- Just send a message → Chat with OpenCode AI (creates persistent session per user)
- `/newchat` - Start a new chat session
- `/clearchat` - Clear current session and start fresh
- `/run <command>` - Run shell command via OpenCode

### PC Control Commands
- `/speak <text>` - Text to speech
- `/sysinfo` - CPU, RAM, disk info
- `/volume <0-100>` - Set volume
- `/brightness <0-100>` - Set brightness
- `/open <app>` - Open app
- `/darkmode on/off` - Toggle dark mode
- `/power saver/balanced/performance` - Set power mode
- `/lock` - Lock screen
- `/screenshot` - Take screenshot
- `/kill <process>` - Kill process
- `/wifi on/off` - Toggle Wi-Fi
- `/search <song>` - Search Spotify

- **Usage**: Message @Open_codebot from anywhere to control your PC and chat with AI

## How to Start Services

### Start OpenCode Server
```bash
# Option 1: Using PowerShell
powershell -Command "Start-Process cmd -ArgumentList '/c opencode serve' -WindowStyle Hidden"

# Option 2: Direct
opencode serve

# Verify: curl http://localhost:4096/global/health
```

### Start Telegram Bot
```bash
# Start bot (requires OpenCode server running first)
python tools/telegram_bot.py

# Or with PowerShell
powershell -Command "Start-Process python -ArgumentList 'C:/Users/Shrey/.config/opencode/tools/telegram_bot.py' -WindowStyle Hidden"

# Check logs
tail -20 D:/workspace/open_code/telegram_bot.log
```

### Quick Status Check
```bash
# Check if OpenCode is running
curl -s http://localhost:4096/global/health

# Check bot logs
tail -20 D:/workspace/open_code/telegram_bot.log
```

### Troubleshooting
- If bot shows "OpenCode not running", restart OpenCode server first
- If Telegram conflicts (409), kill all Python processes and restart bot
- Logs are in: D:/workspace/open_code/telegram_bot.log

## Selenium Tool (Browser Control)

- **Tool location**: C:/Users/Shrey/.config/opencode/tools/selenium_tool.py
- **Requires**: `pip install selenium webdriver-manager`
- **Usage**: Controls a persistent Chrome browser instance.

### Telegram Commands
- `/chrome <url>` - Open Chrome and navigate to a URL.
- `/navigate <url>` - Navigate to a new URL.
- `/click <selector>` - Click on an element using a CSS selector.
- `/type <selector> <text>` - Type text into an element.
- `/gettext <selector>` - Get the text of an element.
- `/title` - Get the current page title and URL.
- `/screenshot` - Take a screenshot of the current page.
- `/closechrome` - Close the Chrome browser instance.

## GitHub CLI Configuration

- **Tool location**: C:\Program Files\GitHub CLI\gh.exe
- **Authentication**: Uses GITHUB_TOKEN environment variable
- **Installation**: winget install --id GitHub.cli -e --source winget
- **Usage**: Direct GitHub repository management via CLI

### Common Commands
```bash
# List all repositories
"C:\Program Files\GitHub CLI\gh.exe" repo list

# View repository details
"C:\Program Files\GitHub CLI\gh.exe" repo view Shrey-211/opencode_configs

# Create an issue
"C:\Program Files\GitHub CLI\gh.exe" issue create --repo Shrey-211/opencode_configs --title "Title" --body "Body"

# List issues
"C:\Program Files\GitHub CLI\gh.exe" issue list --repo Shrey-211/opencode_configs

# Create a pull request
"C:\Program Files\GitHub CLI\gh.exe" pr create --repo Shrey-211/opencode_configs --title "PR Title" --body "PR Body"

# View pull requests
"C:\Program Files\GitHub CLI\gh.exe" pr list --repo Shrey-211/opencode_configs
```

### Environment Setup
- **Token**: GITHUB_TOKEN environment variable (automatically used by gh CLI)
- **Path**: C:\Program Files\GitHub CLI\gh.exe
- **Authentication**: Automatic via environment variable

## YouTube Video Assets
Reference files for recording the "OpenCode Autonomy" video:
- **Plan**: `C:\Users\Shrey\.config\opencode\YOUTUBE_VIDEO_PLAN.md`
- **Script**: `C:\Users\Shrey\.config\opencode\DEMO_SCRIPT.md`

---



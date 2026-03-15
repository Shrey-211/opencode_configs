# OpenCode Autonomy Setup - Complete Capabilities Guide

> **Author**: Shreyas Jadhav (SDET, Pune, India)  
> **Repository**: [Shrey-211/opencode_configs](https://github.com/Shrey-211/opencode_configs)  
> **Video Tutorial**: [YouTube - OpenCode Autonomy](#) *(Coming Soon)*

---

## 🚀 What is This Setup?

This is a **fully autonomous AI agent system** built on OpenCode that allows you to control your entire digital workspace through:

- **🗣️ Voice Commands** - Speak to control your PC
- **📱 Telegram Bot** - Remote control from anywhere
- **🌐 Browser Automation** - Autonomous web interaction
- **🤖 AI Brain** - OpenCode with custom skills and MCP integrations

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
├──────────────┬────────────────┬─────────────────────────────┤
│   Telegram   │    Voice       │      Browser                │
│     Bot      │   Commands     │    Automation               │
└──────┬───────┴───────┬────────┴──────────┬──────────────────┘
       │               │                   │
       ▼               ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE AI BRAIN                        │
│  (Claude/Gemini + Custom Skills + MCP Tools)               │
└──────┬────────────────┬──────────────────┬──────────────────┘
       │                │                  │
       ▼                ▼                  ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
│   System    │ │   Browser    │ │    Voice/STT     │
│   Control   │ │  Automation  │ │   Integration    │
└─────────────┘ └──────────────┘ └──────────────────┘
```

---

## 🔧 Complete Tool Set

### 1. **Text-to-Speech** (`speak.py`)
**Location**: `C:\Users\Shrey\.config\opencode\tools\speak.py`

**Capabilities**:
- Windows Speech Synthesis integration
- Multiple voice options (Microsoft David, Hazel, Zira)
- Asynchronous execution (no blocking)
- Configurable speech rate and volume

**Usage**:
```python
# Via Python
run_tool("speak", {"text": "Hello World", "voice": "en-US-AriaNeural"})

# Via Telegram
/speak Hello from Telegram!
```

---

### 2. **Windows System Control** (`windows.py`)
**Location**: `C:\Users\Shrey\.config\opencode\tools\windows.py`

**20+ System Functions**:

| Category | Functions |
|----------|-----------|
| **Audio** | Volume control, Mute/Unmute |
| **Display** | Brightness control, Dark mode toggle |
| **Network** | Wi-Fi on/off, Bluetooth on/off, Network info |
| **System** | Sysinfo (CPU, RAM, Disk), Battery status |
| **Apps** | Open apps, Open folders, Open settings |
| **Security** | Lock screen, Sleep, Shutdown, Restart |
| **Processes** | Kill process, List running processes |
| **Utilities** | Screenshot, Clipboard operations, Night light |

**Usage Examples**:
```bash
# Telegram Commands
/volume 50                    # Set volume to 50%
/brightness 80                # Set brightness to 80%
/darkmode on                  # Enable dark mode
/sysinfo                      # Get system information
/lock                         # Lock screen
/screenshot                   # Take screenshot
/kill chrome                  # Kill Chrome process
```

---

### 3. **Browser Automation** (`selenium_tool.py`)
**Location**: `C:\Users\Shrey\.config\opencode\tools\selenium_tool.py`

**Features**:
- Persistent Chrome browser instance
- Non-blocking execution
- YouTube video playback support

**Capabilities**:
- Open/Close browser
- Navigate to URLs
- Click elements (CSS selectors)
- Type text into forms
- Extract text/attributes
- Take screenshots
- Execute JavaScript
- Play YouTube videos

**Usage Examples**:
```bash
# Telegram Commands
/chrome https://github.com             # Open Chrome and navigate
/navigate https://google.com           # Navigate to URL
/click button.submit                   # Click element
/type input.search "OpenCode AI"       # Type text
/gettext .result-title                 # Get element text
/screenshot                            # Take browser screenshot
/youtube "lofi hip hop"                # Play YouTube video
```

---

### 4. **Speech-to-Text** (`listen.py`)
**Location**: `C:\Users\Shrey\.config\opencode\tools\listen.py`

**Features**:
- Google Speech Recognition API
- Ambient noise adjustment
- Configurable timeout and phrase limits
- Multi-language support

**Usage**:
```python
# Via Python
run_tool("listen", {"timeout": 10, "language": "en-US"})

# Returns recognized speech text
```

---

### 5. **Telegram Bot** (`telegram_bot.py`)
**Location**: `C:\Users\Shrey\.config\opencode\tools\telegram_bot.py`

**Bot Username**: `@Open_codebot`  
**Token**: `8783206801:AAFNPEoOdOcFVFbzjam4t8ZyLutiW1MaEdc`

**AI Chat Commands**:
- `/newchat` - Start new AI session
- `/clearchat` - Clear current session
- `/run <command>` - Run shell commands
- Just send a message - Chat with AI

**PC Control Commands**:
- `/speak <text>` - Text to speech
- `/sysinfo` - System information
- `/volume <0-100>` - Set volume
- `/brightness <0-100>` - Set brightness
- `/open <app>` - Open application
- `/darkmode on/off` - Toggle dark mode
- `/power saver/balanced/performance` - Set power mode
- `/lock` - Lock screen
- `/screenshot` - Take screenshot
- `/kill <process>` - Kill process
- `/wifi on/off` - Toggle Wi-Fi
- `/search <song>` - Search Spotify

**Browser Commands**:
- `/chrome <url>` - Open Chrome & navigate
- `/navigate <url>` - Navigate to URL
- `/click <selector>` - Click element
- `/type <selector> <text>` - Type text
- `/gettext <selector>` - Get element text
- `/title` - Get page title & URL
- `/screenshot` - Take browser screenshot
- `/closechrome` - Close browser
- `/youtube <song>` - Play YouTube video

---

### 6. **OpenCode MCP Integrations** (`opencode.json`)

**Configured MCPs**:
1. **Playwright** - Browser automation
2. **Filesystem** - File operations (D:/workspace, C:/Users/Shrey)
3. **Memory** - Persistent knowledge graph
4. **GitHub** - Repository management
5. **Scrapling** - Web scraping
6. **Context7** - Documentation lookup

**Configured Skills**:
- `find-skills` - Discover available skills
- `web-design-guidelines` - UI/UX review
- `vercel-react-best-practices` - React optimization
- `typescript-best-practices` - TypeScript patterns
- `bug-fix` - Systematic bug fixing workflow

---

## 🎯 What You Can Achieve

### Level 1: Remote PC Control
**From anywhere in the world, via Telegram:**

✅ Check system status (CPU, RAM, Disk)  
✅ Control audio volume and brightness  
✅ Lock your screen remotely  
✅ Take screenshots  
✅ Open applications  
✅ Toggle dark mode and power settings  
✅ Manage network (Wi-Fi/Bluetooth)  

**Example Scenario**:
> You're away from home and want to check if your PC is running. Send `/sysinfo` to @Open_codebot and instantly get system stats.

---

### Level 2: Voice-Activated Control
**Speak commands to control your PC:**

✅ "Open Chrome and search for OpenCode"  
✅ "Set volume to 50 percent"  
✅ "Take a screenshot"  
✅ "Lock my screen"  

**Example Scenario**:
> While cooking, you say "Open YouTube and play lofi hip hop" - your PC handles it hands-free.

---

### Level 3: Autonomous Browser Automation
**Let AI control your web browsing:**

✅ Navigate to any website  
✅ Click buttons and links automatically  
✅ Fill forms and submit data  
✅ Extract information from pages  
✅ Take screenshots of web pages  
✅ Play YouTube videos  

**Example Scenario**:
> "Find the latest news on AI and read the first headline" - AI searches, extracts, and reads back to you.

---

### Level 4: AI-Powered Development
**Code with AI assistance:**

✅ Natural language to code conversion  
✅ Automated testing and debugging  
✅ Git repository management  
✅ Code review and optimization  
✅ Documentation generation  

**Example Scenario**:
> "Create a React component for a login form with validation" - AI generates complete, tested code.

---

### Level 5: Complete Automation Workflows
**Chain multiple actions together:**

✅ "Check my PC status, then open Chrome and search for job postings, then take screenshots of top 3 results"  
✅ "Lock my screen, start a backup, and notify me when done"  
✅ "Open VS Code, create a new project, and set up the boilerplate"  

---

## 📁 Project Structure

```
C:\Users\Shrey\.config\opencode\
├── opencode.json              # MCP & Skills configuration
├── AGENTS.md                  # Agent instructions & rules
├── CAPABILITIES.md            # This file
├── YOUTUBE_VIDEO_PLAN.md      # Video production plan
├── DEMO_SCRIPT.md             # Video demonstration script
├── package.json               # Node.js dependencies
└── tools/
    ├── speak.py               # Text-to-speech
    ├── listen.py              # Speech-to-text
    ├── windows.py             # System control
    ├── selenium_tool.py       # Browser automation
    ├── telegram_bot.py        # Telegram interface
    ├── spotify.py             # Spotify control
    ├── webhook.py             # HTTP API server
    └── __pycache__/           # Python cache
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js
- OpenCode installed
- Chrome browser (for automation)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Shrey-211/opencode_configs.git
   cd opencode_configs
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start OpenCode server**:
   ```bash
   opencode serve
   ```

4. **Start Telegram bot**:
   ```bash
   python tools/telegram_bot.py
   ```

5. **Send /start to @Open_codebot on Telegram**

---

## 🔐 Security Notes

- **Telegram Token**: Currently hardcoded - consider using environment variables
- **Filesystem Access**: Limited to D:/workspace and C:/Users/Shrey
- **GitHub Access**: Uses GITHUB_TOKEN environment variable
- **Voice Recognition**: Uses Google Speech API (requires internet)

---

## 📊 Performance Metrics

- **Voice Response Time**: ~1-2 seconds
- **Telegram Response Time**: ~2-5 seconds (depends on AI processing)
- **Browser Automation**: Instant (persistent session)
- **System Commands**: <1 second

---

## 🎓 Learning Path

1. **Beginner**: Start with Telegram commands
2. **Intermediate**: Add voice commands
3. **Advanced**: Create custom MCP tools
4. **Expert**: Build complete automation workflows

---

## 🤝 Contributing

This is an open project! You can:

1. Fork the repository
2. Add new tools to the `tools/` directory
3. Create new MCP integrations
4. Improve existing capabilities
5. Share your automation workflows

---

## 📚 Resources

- **OpenCode Documentation**: [opencode.ai](https://opencode.ai)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io)
- **Selenium Documentation**: [selenium.dev](https://www.selenium.dev)
- **Telegram Bot API**: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)

---

## 🎬 Video Demo Script

For the complete video demonstration script, see:
- `YOUTUBE_VIDEO_PLAN.md` - Production plan
- `DEMO_SCRIPT.md` - Step-by-step commands

---

## 📝 License

MIT License - Feel free to use and modify.

---

**Built with ❤️ by Shreyas Jadhav**  
*AI-First Developer | SDET | Automation Enthusiast*

---
*Last Updated: March 15, 2026*

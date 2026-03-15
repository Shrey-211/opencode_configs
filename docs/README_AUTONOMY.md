# OpenCode Autonomy System v2

> **Author**: Shreyas Jadhav (SDET, Pune, India)  
> **Repository**: [Shrey-211/opencode_configs](https://github.com/Shrey-211/opencode_configs)  
> **Version**: 2.0 (Goal-Driven Autonomy)

---

## 🚀 Overview

This is a **goal-driven autonomous AI agent system** built on OpenCode that evolves from command-driven automation to intelligent goal execution.

### Key Improvements from v1

| Feature | v1 (Command-Driven) | v2 (Goal-Driven) |
|---------|---------------------|------------------|
| **Interface** | Specific commands (`/chrome`, `/click`) | Natural language goals (`/goal Open browser...`) |
| **Execution** | Single action per command | Multi-step planning & execution |
| **Observation** | No feedback loop | Vision-based observation & adaptation |
| **Memory** | Basic memory MCP | Persistent context & preferences |
| **Background Tasks** | Synchronous execution | Async task queue with progress tracking |
| **Security** | Hardcoded tokens | Environment variables + command confirmations |
| **Monitoring** | Manual checks | Automated system monitoring with alerts |
| **Architecture** | Single agent | Multi-agent coordination |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Telegram)                 │
├──────────────────────┬──────────────────────────────────────┤
│   /goal <task>       │   /do <task>                         │
│   Natural Language   │   Direct Command                     │
└──────────┬───────────┴──────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│              MULTI-AGENT COORDINATION LAYER                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Planner   │  │   Executor  │  │   Observer  │         │
│  │   Agent     │  │    Agent    │  │    Agent    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────┬──────────────────────────────────────┘
           │           │           │
           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│                   TOOL EXECUTION LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Browser   │  │   System    │  │   Memory    │         │
│  │  Automation │  │   Control   │  │    MCP      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Redis    │  │   Task      │  │   System    │         │
│  │  (Queue)    │  │   Queue     │  │  Monitoring │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 New Commands

### Goal Execution

**/goal** - Execute a complex goal using multi-agent system
```
/goal Open browser and search for Python tutorials
/goal Check my system status and take a screenshot
/goal Extract text from GitHub and save to file
```

**/do** - Execute a natural language task
```
/do Take a screenshot of the current page
/do Run a command to list files
/do Check system resources
```

### System Control

**/run** - Run shell command (with confirmation for dangerous commands)
```
/run ls -la
/run git status
```

**/sysinfo** - Check system status
```
/sysinfo
```

### Chat Management

**/newchat** - Start new AI session
**/clearchat** - Clear current session

---

## 📁 Project Structure

```
C:\Users\Shrey\.config\opencode\
├── .env                            # Environment variables (NEW)
├── config_loader.py                # Configuration loader (NEW)
├── security.py                     # Security manager (NEW)
├── task_queue.py                   # Background task queue (NEW)
├── requirements.txt                # Python dependencies (UPDATED)
│
├── agents/                         # Multi-agent system (NEW)
│   ├── __init__.py
│   ├── planner.py                  # Goal planning agent
│   ├── executor.py                 # Task execution agent
│   └── observer.py                 # Result validation agent
│
├── multiagent/                     # Agent coordination (NEW)
│   └── coordinator.py              # Multi-agent coordinator
│
├── nlp/                            # Natural language processing (NEW)
│   └── task_parser.py              # Task parsing from natural language
│
├── monitoring/                     # System monitoring (NEW)
│   └── daemon.py                   # Monitoring daemon
│
├── memory/                         # Memory management (NEW)
│
├── tools/                          # Original tools (UPDATED)
│   ├── telegram_bot_v2.py          # NEW integrated Telegram bot
│   ├── speak.py
│   ├── windows.py
│   ├── selenium_tool.py
│   └── ...
│
├── CAPABILITIES.md                 # Complete capabilities guide
├── YOUTUBE_VIDEO_PLAN.md           # Video production plan
├── DEMO_SCRIPT.md                  # Video demonstration script
└── README_AUTONOMY.md              # This file
```

---

## 🔧 Installation & Setup

### 1. Configure Environment

Create `.env` file:
```bash
# Telegram Bot
TELEGRAM_TOKEN=your_token_here

# AI APIs (optional)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# System Monitoring Thresholds
CPU_THRESHOLD=90
RAM_THRESHOLD=85
DISK_THRESHOLD=90

# Security
REQUIRE_CONFIRMATION=true
DANGEROUS_COMMANDS=shutdown,restart,kill,rm,format,mkfs
ALLOWED_CHAT_IDS=  # Empty = allow all chats

# Paths
WORKSPACE_PATH=D:/workspace/open_code
SCREENSHOT_DIR=D:/workspace/open_code/screenshots
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Redis (Required for Task Queue)

```bash
# Windows
redis-server

# Or download from: https://github.com/tporadowski/redis/releases
```

### 4. Start OpenCode Server

```bash
opencode serve
```

### 5. Start Telegram Bot v2

```bash
python tools/telegram_bot_v2.py
```

---

## 🎮 Usage Examples

### Example 1: Goal-Driven Execution

**User:** `/goal Open browser and search for AI jobs`

**Agent Workflow:**
1. **Planner** creates plan:
   - Step 1: Open browser to Google
   - Step 2: Type "AI jobs" in search
   - Step 3: Click search button
   - Step 4: Take screenshot

2. **Executor** runs each step
3. **Observer** validates outcomes
4. **Coordinator** reports success

**Result:** "✅ Goal completed in 45 seconds"

### Example 2: Natural Language Task

**User:** `/do Take a screenshot and save it`

**Agent Workflow:**
1. **Parser** extracts tool calls:
   - `screenshot()` action
   - `save_to_file()` action

2. **Executor** runs actions
3. **Observer** confirms file saved

**Result:** "✅ Screenshot saved to D:/workspace/open_code/screenshots/"

### Example 3: System Monitoring

**Background:** Every 5 minutes, monitoring daemon checks:
- CPU usage > 90% → Alert sent to Telegram
- RAM usage > 85% → Alert sent to Telegram
- Disk usage > 90% → Alert sent to Telegram

---

## 🔒 Security Features

### 1. Environment Variables
- All secrets stored in `.env` file
- Never commit `.env` to version control
- Use environment variables for deployment

### 2. Chat ID Whitelisting
```bash
ALLOWED_CHAT_IDS=123456789,987654321
```

### 3. Command Confirmation
Dangerous commands require user confirmation:
- `shutdown`, `restart`, `kill`, `rm`, `format`
- Confirmation via inline buttons in Telegram

### 4. Audit Logging
All commands logged to `audit_log.txt`:
```
2026-03-15T10:30:00 | Chat: 123456789 | Command: /run rm -rf / | Status: DENIED
```

---

## 📊 Monitoring & Alerts

### System Metrics Collected
- CPU usage (percent)
- Memory usage (percent and available GB)
- Disk usage (percent and free GB)
- Network I/O (sent/received MB)
- CPU temperature (if available)

### Alert Thresholds
Configurable in `.env`:
- `CPU_THRESHOLD=90`
- `RAM_THRESHOLD=85`
- `DISK_THRESHOLD=90`

### Alert Delivery
Alerts sent via Telegram when thresholds exceeded.

---

## 🧠 Multi-Agent Architecture

### Planner Agent
- **Purpose**: Break down goals into executable steps
- **Input**: Natural language goal
- **Output**: Structured plan with steps
- **Tools**: AI-powered planning (OpenCode/Gemini)

### Executor Agent
- **Purpose**: Execute planned steps
- **Input**: Plan steps
- **Output**: Execution results
- **Tools**: Browser automation, system commands, file operations

### Observer Agent
- **Purpose**: Validate execution outcomes
- **Input**: Execution results
- **Output**: Validation status + suggested fixes
- **Tools**: Result analysis, error detection

### Coordinator
- **Purpose**: Orchestrate agent collaboration
- **Workflow**: Planner → Executor → Observer → (Adapt if needed)

---

## 🚀 Background Task Queue

### Features
- Async task execution with Arq + Redis
- Progress tracking via Redis pub/sub
- Telegram integration for real-time updates
- Persistent storage across bot restarts

### Example Tasks
```python
# Browser automation (long-running)
await task_queue.enqueue_task("browser_automation_task", url, chat_id)

# System check
await task_queue.enqueue_task("system_check_task", chat_id)

# Custom background task
await task_queue.enqueue_task("long_running_task", chat_id, duration=10)
```

### Progress Updates
Tasks publish progress to Redis channel `telegram:{chat_id}`:
```
🔄 Starting browser automation...
📊 Progress: 10%
📊 Progress: 50%
✅ Task completed!
```

---

## 📈 Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Goal Planning | 1-3s | AI-powered planning |
| Task Execution | Varies | Depends on complexity |
| System Check | <1s | Local execution |
| Background Tasks | Async | No blocking |
| Monitoring | 5min intervals | Configurable |

---

## 🔧 Troubleshooting

### Redis Not Running
```bash
# Start Redis
redis-server

# Verify connection
redis-cli ping
```

### OpenCode Server Not Running
```bash
opencode serve
curl http://localhost:4096/global/health
```

### Telegram Bot Errors
```bash
# Check logs
tail -f telegram_bot_v2.log

# Verify token
echo $TELEGRAM_TOKEN
```

### Permission Denied
- Check `ALLOWED_CHAT_IDS` in `.env`
- Verify chat ID is in whitelist

---

## 📚 API Reference

### ConfigLoader
```python
from config_loader import config

config.TELEGRAM_TOKEN
config.is_allowed_chat(chat_id)
config.requires_confirmation(command)
config.get_redis_url()
```

### SecurityManager
```python
from security import security_manager

security_manager.is_command_allowed(chat_id, command)
security_manager.requires_confirmation(command)
security_manager.audit_log(chat_id, command, success, details)
```

### TaskQueue
```python
from task_queue import task_queue

await task_queue.enqueue_task(task_name, *args, **kwargs)
await task_queue.get_task_status(task_id)
```

### MultiAgentCoordinator
```python
from multiagent.coordinator import coordinator

await coordinator.execute_goal(goal, user_id)
await coordinator.execute_multi_step_goal(goal, user_id)
```

---

## 🎬 Video Demo Script

For the complete video demonstration, see:
- `YOUTUBE_VIDEO_PLAN.md` - Production plan
- `DEMO_SCRIPT.md` - Step-by-step commands

---

## 📝 Development Roadmap

### Phase 1: Foundation (Complete ✅)
- Environment configuration
- Security layer
- Task queue system
- Multi-agent architecture

### Phase 2: Intelligence (Future)
- Vision model integration for observation
- Self-healing browser automation
- Advanced NLP with LLM

### Phase 3: Scale (Future)
- Multi-user support
- Cloud deployment
- Performance optimization

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - Feel free to use and modify.

---

**Built with ❤️ by Shreyas Jadhav**  
*AI-First Developer | SDET | Automation Enthusiast*

---
*Last Updated: March 15, 2026*

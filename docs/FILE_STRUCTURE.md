# File Structure - OpenCode Autonomy System v2

## Root Directory
```
C:\Users\Shrey\.config\opencode\
├── __init__.py                      # Main package initialization
├── .env                             # Environment variables (SECRET)
├── .gitignore                       # Git ignore rules
├── opencode.json                    # OpenCode configuration
├── package.json                     # Node.js dependencies
├── requirements.txt                 # Python dependencies
├── skills-lock.json                 # Skills configuration
├── AGENTS.md                        # Agent instructions
├── README.md                        # Project README
├── telegram_bot_v2.log              # Bot logs
│
├── docs/                            # Documentation
│   ├── __init__.py
│   ├── CAPABILITIES.md              # Complete capabilities guide
│   ├── FILE_STRUCTURE.md            # This file
│   ├── IMPLEMENTATION_SUMMARY.md    # Implementation summary
│   ├── README_AUTONOMY.md           # Comprehensive documentation
│   ├── YOUTUBE_VIDEO_PLAN.md        # Video production plan
│   └── DEMO_SCRIPT.md               # Video demo script
│
├── utils/                           # Utility modules
│   ├── __init__.py                  # Utils package init
│   ├── config_loader.py             # Configuration management
│   ├── security.py                  # Security management
│   ├── task_queue.py                # Background task queue
│   ├── test_integration.py          # Integration tests
│   └── verify_bot.py                # Bot verification script
│
├── agents/                          # Multi-agent system
│   ├── __init__.py                  # Agents package init
│   ├── planner.py                   # Goal planning agent
│   ├── executor.py                  # Task execution agent
│   └── observer.py                  # Result validation agent
│
├── multiagent/                      # Agent coordination
│   └── coordinator.py               # Multi-agent coordinator
│
├── nlp/                             # Natural language processing
│   └── task_parser.py               # Task parsing from natural language
│
├── monitoring/                      # System monitoring
│   └── daemon.py                    # Monitoring daemon
│
├── memory/                          # Memory management (placeholder)
│
├── tools/                           # External tools
│   ├── __init__.py
│   ├── speak.py                     # Text-to-speech
│   ├── listen.py                    # Speech-to-text
│   ├── windows.py                   # Windows system control
│   ├── selenium_tool.py             # Browser automation
│   ├── telegram_bot.py              # Original Telegram bot (v1)
│   ├── telegram_bot_v2.py           # NEW Integrated Telegram bot (v2)
│   ├── spotify.py                   # Spotify control
│   └── webhook.py                   # HTTP API server
│
└── __pycache__/                     # Python cache
```

## Key Changes from Original Structure

### Before (v1)
- All files in root directory
- Hardcoded configuration
- No proper package structure

### After (v2)
- Organized into logical packages
- Environment-based configuration
- Proper import structure
- Clear separation of concerns

## Package Dependencies

```
utils → (no dependencies)
agents → utils
multiagent → agents
nlp → utils
monitoring → utils
tools → utils, agents, multiagent, nlp, monitoring
```

## Running the System

1. **Start Redis** (if not running)
2. **Start OpenCode Server**: `opencode serve`
3. **Start Telegram Bot**: `python tools/telegram_bot_v2.py`
4. **Run Tests**: `python utils/test_integration.py`

## File Organization Rules

1. **utils/** - Shared utilities and configuration
2. **agents/** - Individual agent implementations
3. **multiagent/** - Agent coordination logic
4. **nlp/** - Natural language processing
5. **monitoring/** - System monitoring
6. **tools/** - External tool integrations
7. **docs/** - Documentation files
8. **memory/** - Persistent storage (placeholder)

# OpenCode Configuration and Tools

This repository contains the configuration files and custom tools for OpenCode.

## Structure

-  - Agent instructions and configuration
-  - MCP server configuration
-  - Node.js dependencies
-  - Custom automation tools

## Tools

### Speech Tools
-  - Text-to-speech using Windows Speech Synthesis
-  - Speech-to-text using Google Speech API

### System Control
-  - Windows system control (volume, brightness, apps, etc.)

### Remote Control
-  - Telegram bot for remote control
-  - Webhook server for HTTP control

### Browser Automation
-  - Persistent Chrome browser control

### Media Control
-  - Spotify integration
-  - YouTube playback

## Usage

### Start OpenCode Server
```bash
opencode serve
```

### Start Telegram Bot
```bash
python tools/telegram_bot.py
```

### Use Speak Tool
```bash
echo {text: Hello World} | python tools/speak.py
```

## Installation

1. Clone this repository to `C:\Users\Shrey\.config\opencode`
2. Install dependencies: `npm install`
3. Start OpenCode server
4. Start Telegram bot (optional)

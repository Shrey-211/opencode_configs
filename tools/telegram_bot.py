#!/usr/bin/env python3
"""
Telegram bot to control opencode remotely.
Uses OpenCode REST API to create persistent sessions per user.
"""

import os
import json
import asyncio
import aiohttp
import logging
from telegram import Update

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOOLS_DIR = "C:/Users/Shrey/.config/opencode/tools"

# Load token from environment or use default
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8783206801:AAFNPEoOdOcFVFbzjam4t8ZyLutiW1MaEdc")

OPENCODE_BASE_URL = "http://localhost:4096"

user_sessions = {}

tool_map = {
    "speak": "speak.py",
    "listen": "listen.py",
    "windows": "windows.py",
    "spotify": "spotify.py",
    "selenium": "selenium_tool.py",
}


class OpenCodeClient:
    def __init__(self, base_url: str = OPENCODE_BASE_URL):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def health_check(self) -> bool:
        try:
            async with self.session.get(f"{self.base_url}/global/health") as resp:
                return resp.status == 200
        except:
            return False
    
    async def create_session(self, title: str = "Telegram Chat", directory: str = "D:/workspace/open_code") -> dict:
        try:
            async with self.session.post(
                f"{self.base_url}/session",
                json={"title": title, "directory": directory}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    session_id = data.get("id")
                    if session_id:
                        return {"session_id": session_id, "data": data}
                    return {"error": "No session ID in response"}
                return {"error": f"Failed to create session: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_prompt(self, session_id: str, text: str, directory: str = "D:/workspace/open_code") -> dict:
        try:
            payload = {
                "parts": [{"type": "text", "text": text}],
                "directory": directory
            }
            logger.info(f"Sending prompt to session {session_id}: {text}")
            async with self.session.post(
                f"{self.base_url}/session/{session_id}/message",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"Response status: {resp.status}, data keys: {data.keys()}")
                    return self._extract_response(data)
                logger.error(f"Request failed with status: {resp.status}")
                return {"error": f"Request failed: {resp.status}"}
        except Exception as e:
            logger.exception(f"Exception in send_prompt: {e}")
            return {"error": str(e)}
    
    async def run_shell(self, session_id: str, command: str, directory: str = "D:/workspace/open_code") -> dict:
        try:
            payload = {
                "parts": [{"type": "text", "text": command}],
                "shell": True,
                "directory": directory
            }
            async with self.session.post(
                f"{self.base_url}/session/{session_id}/shell",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._extract_response(data)
                return {"error": f"Shell failed: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_session(self, session_id: str) -> bool:
        try:
            async with self.session.delete(f"{self.base_url}/session/{session_id}") as resp:
                return resp.status == 200
        except:
            return False
    
    async def list_sessions(self) -> list:
        try:
            async with self.session.get(f"{self.base_url}/session") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                return []
        except:
            return []
    
    def _extract_response(self, data: dict) -> dict:
        logger.info(f"DEBUG: Raw response keys: {data.keys()}")
        
        parts = data.get("parts", [])
        if not parts:
            parts = data.get("data", {}).get("parts", [])
        
        logger.info(f"DEBUG: Found {len(parts)} parts")
        
        if parts:
            text_parts = []
            for part in parts:
                part_type = part.get("type")
                logger.info(f"DEBUG: Part type: {part_type}")
                if part_type == "text":
                    text_parts.append(part.get("text", ""))
                elif part_type == "tool_use":
                    text_parts.append(f"[Tool: {part.get('name', 'unknown')}]")
                elif part_type == "tool_result":
                    text_parts.append(f"[Tool Result]")
                elif part_type == "reasoning":
                    text_parts.append(f"[Reasoning: {part.get('text', '')[:100]}]")
            
            logger.info(f"DEBUG: text_parts: {text_parts}")
            full_text = "\n".join(text_parts)
            if len(full_text) > 4000:
                full_text = full_text[:4000] + "\n\n[Response truncated...]"
            return {"response": full_text}
        
        info = data.get("info", {})
        if info.get("error"):
            return {"error": info["error"].get("message", str(info["error"]))}
        
        return {"response": "No response generated"}


opencode_client = None


async def get_opencode() -> OpenCodeClient:
    global opencode_client
    if opencode_client is None:
        opencode_client = OpenCodeClient()
    return opencode_client


def run_tool(tool_name: str, params: dict) -> dict:
    if tool_name not in tool_map:
        return {"error": f"Unknown tool: {tool_name}"}
    
    tool_file = tool_map[tool_name]
    
    if tool_name == "speak":
        if "text" not in params:
            return {"error": "Missing text parameter"}
        input_data = json.dumps({
            "text": params.get("text"),
            "voice": params.get("voice", "en-US-AriaNeural"),
            "rate": params.get("rate", "+0%"),
            "volume": params.get("volume", "+0%")
        })
    elif tool_name == "listen":
        input_data = json.dumps({
            "timeout": params.get("timeout", 10),
            "phrase_limit": params.get("phrase_limit", 5),
            "language": params.get("language", "en-US")
        })
    elif tool_name == "windows":
        input_data = json.dumps(params)
    elif tool_name == "spotify":
        input_data = json.dumps(params)
    else:
        input_data = json.dumps(params)
    
    import subprocess
    try:
        result = subprocess.run(
            ["python", f"{TOOLS_DIR}/{tool_file}"],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=60
        )
        try:
            return json.loads(result.stdout)
        except:
            return {"raw_output": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm connected to OpenCode AI. You can chat with AI and control your PC!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/speak <text> - Text to speech\n"
        "/newchat - Start a new chat session\n"
        "/clearchat - Clear current chat\n"
        "/sysinfo - Get system info\n"
        "/run <command> - Run shell command\n"
        "/help - Show all commands\n\n"
        "Just send a message to chat with AI!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n\n"
        "🤖 AI Chat:\n"
        "/newchat - Start new chat session\n"
        "/clearchat - Clear current session\n"
        "/run <cmd> - Run shell command\n"
        "Just chat with me!\n\n"
        "💻 PC Control:\n"
        "/speak <text> - Text to speech\n"
        "/sysinfo - CPU, RAM, disk info\n"
        "/volume <level> - Set volume 0-100\n"
        "/brightness <level> - Set brightness 0-100\n"
        "/open <app> - Open app\n"
        "/darkmode on/off - Toggle dark mode\n"
        "/lock - Lock screen\n"
        "/screenshot - Take screenshot\n"
        "/kill <process> - Kill process\n"
        "/wifi on/off - Toggle Wi-Fi\n"
        "/search <song> - Search Spotify\n\n"
        "🌐 Browser (Selenium):\n"
        "/chrome <url> - Open Chrome & navigate to URL\n"
        "/navigate <url> - Navigate to URL\n"
        "/click <selector> - Click element\n"
        "/type <selector> <text> - Type text\n"
        "/gettext <selector> - Get element text\n"
        "/title - Get page title & URL\n"
        "/screenshot - Take browser screenshot\n"
        "/closechrome - Close browser\n"
        "/youtube <song> - Play YouTube video (non-blocking)"
    )


async def newchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    client = await get_opencode()
    
    session = await client.create_session(title=f"Telegram User {user_id}")
    
    if "error" in session:
        await update.message.reply_text(f"Failed to create session: {session['error']}")
        return
    
    session_id = session.get("data", {}).get("id")
    user_sessions[user_id] = session_id
    
    await update.message.reply_text(
        f"✅ New chat session created!\n\n"
        f"Session ID: {session_id[:8]}...\n"
        f"You can now chat with AI!"
    )


async def clearchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id in user_sessions:
        client = await get_opencode()
        old_session_id = user_sessions[user_id]
        await client.delete_session(old_session_id)
        del user_sessions[user_id]
        
        await update.message.reply_text("✅ Chat session cleared! Use /newchat to start fresh.")
    else:
        await update.message.reply_text("No active session. Use /newchat to start chatting!")


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return
    
    command = " ".join(context.args)
    user_id = str(update.effective_user.id)
    
    await update.message.reply_text(f"Running: `{command}`...", parse_mode="Markdown")
    
    client = await get_opencode()
    
    if user_id not in user_sessions:
        session = await client.create_session(title=f"Telegram Shell {user_id}")
        if "error" in session:
            await update.message.reply_text(f"Failed: {session['error']}")
            return
        user_sessions[user_id] = session.get("data", {}).get("id")
    
    session_id = user_sessions[user_id]
    result = await client.run_shell(session_id, command)
    
    if "error" in result:
        await update.message.reply_text(f"Error: {result['error']}")
    else:
        response = result.get("response", "No output")
        if len(response) > 4000:
            response = response[:4000] + "\n\n[Truncated]"
        await update.message.reply_text(f"```\n{response}\n```", parse_mode="MarkdownV2")


async def speak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /speak <text>")
        return
    
    result = run_tool("speak", {"text": text})
    await update.message.reply_text(f"🔊 Speaking: {text}")


async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("windows", {"action": "sysinfo"})
    if "info" in result:
        info = result["info"]
        msg = f"CPU: {info.get('cpu', 'N/A')}\nRAM: {info.get('memory_gb', 'N/A')} GB\nDisk: {info.get('disk_free_g', 'N/A')} GB free"
    else:
        msg = str(result)
    await update.message.reply_text(msg)


async def volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /volume <0-100>")
        return
    try:
        level = int(context.args[0])
        result = run_tool("windows", {"action": "volume", "level": level})
        await update.message.reply_text(result.get("message", str(result)))
    except ValueError:
        await update.message.reply_text("Usage: /volume <0-100>")


async def brightness_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /brightness <0-100>")
        return
    try:
        level = int(context.args[0])
        result = run_tool("windows", {"action": "brightness", "level": level})
        await update.message.reply_text(result.get("message", str(result)))
    except ValueError:
        await update.message.reply_text("Usage: /brightness <0-100>")


async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /open <app>")
        return
    app = context.args[0]
    result = run_tool("windows", {"action": "open", "app": app})
    await update.message.reply_text(result.get("message", str(result)))


async def darkmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /darkmode on or /darkmode off")
        return
    enable = context.args[0].lower() == "on"
    result = run_tool("windows", {"action": "darkmode", "enable": enable})
    await update.message.reply_text(result.get("message", str(result)))


async def power_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /power saver/balanced/performance")
        return
    mode = context.args[0].lower()
    result = run_tool("windows", {"action": "power", "mode": mode})
    await update.message.reply_text(result.get("message", str(result)))


async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("windows", {"action": "lock"})
    await update.message.reply_text("🔒 Screen locked!")


async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("windows", {"action": "screenshot"})
    await update.message.reply_text(result.get("message", str(result)))


async def kill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /kill <process_name>")
        return
    name = context.args[0]
    result = run_tool("windows", {"action": "kill", "name": name})
    await update.message.reply_text(result.get("message", str(result)))


async def wifi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /wifi on or /wifi off")
        return
    enable = context.args[0].lower() == "on"
    result = run_tool("windows", {"action": "wifi", "enable": enable})
    await update.message.reply_text(result.get("message", str(result)))


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <song>")
        return
    query = " ".join(context.args)
    result = run_tool("spotify", {"action": "search", "query": query})
    if "results" in result:
        songs = result["results"][:5]
        msg = "Search results:\n"
        for i, song in enumerate(songs, 1):
            msg += f"{i}. {song['name']} - {song['artist']}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(str(result))


async def chrome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args) if context.args else "about:blank"
    result = run_tool("selenium", {"action": "open", "url": url})
    if result.get("status") == "success":
        await update.message.reply_text(f"✅ {result.get('message')}\n\nTitle: {result.get('title', 'N/A')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def navigate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /navigate <url>")
        return
    url = " ".join(context.args)
    result = run_tool("selenium", {"action": "navigate", "url": url})
    if result.get("status") == "success":
        await update.message.reply_text(f"✅ {result.get('message')}\n\nTitle: {result.get('title', 'N/A')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def click_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /click <css_selector>")
        return
    selector = " ".join(context.args)
    result = run_tool("selenium", {"action": "click", "selector": selector})
    if result.get("status") == "success":
        await update.message.reply_text(f"✅ {result.get('message')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def type_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /type <selector> <text>")
        return
    selector = context.args[0]
    text = " ".join(context.args[1:])
    result = run_tool("selenium", {"action": "type", "selector": selector, "text": text})
    if result.get("status") == "success":
        await update.message.reply_text(f"✅ {result.get('message')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def gettext_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /gettext <css_selector>")
        return
    selector = " ".join(context.args)
    result = run_tool("selenium", {"action": "get_text", "selector": selector})
    if result.get("status") == "success":
        await update.message.reply_text(f"📝 Text: {result.get('text', '')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def pagetitle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("selenium", {"action": "title"})
    if result.get("status") == "success":
        await update.message.reply_text(f"📑 Title: {result.get('title', 'N/A')}\n🔗 URL: {result.get('url', 'N/A')}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def chrome_screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("selenium", {"action": "screenshot"})
    if result.get("status") == "success":
        filepath = result.get("filepath", "")
        try:
            await update.message.reply_photo(photo=filepath, caption=f"📸 Screenshot saved")
        except Exception as e:
            await update.message.reply_text(f"✅ {result.get('message')}\n\nPath: {filepath}")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def chromeclose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_tool("selenium", {"action": "close"})
    await update.message.reply_text(f"🔴 {result.get('message', str(result))}")


async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /youtube <song_name> or /youtube <video_id>")
        return
    
    query = " ".join(context.args)
    
    # Check if it's a direct video ID (11 characters)
    if len(query) == 11 and all(c.isalnum() for c in query):
        video_id = query
        url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        # Search for the song on YouTube
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        await update.message.reply_text(f"🔍 Searching YouTube for: {query}")
        
        # Open Chrome and navigate to search results
        result = run_tool("selenium", {"action": "open", "url": search_url})
        if result.get("status") != "success":
            await update.message.reply_text(f"❌ {result.get('message', str(result))}")
            return
        
        # Wait a bit for page to load
        import time
        time.sleep(3)
        
        # Try to get the first video link from page source
        try:
            import subprocess
            result = subprocess.run(
                ["python", f"{TOOLS_DIR}/selenium_tool.py"],
                input=json.dumps({"action": "html"}),
                capture_output=True,
                text=True,
                timeout=30
            )
            html = json.loads(result.stdout).get("html", "")
            
            # Extract first video ID from search results
            import re
            # Look for /watch?v=VIDEO_ID patterns
            matches = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
            if matches:
                video_id = matches[0]
                url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                await update.message.reply_text("❌ Could not find video in search results. Try a more specific query.")
                return
        except Exception as e:
            await update.message.reply_text(f"❌ Error searching: {str(e)}")
            return
    
    # Play the YouTube video asynchronously
    result = run_tool("selenium", {"action": "play_youtube", "video_id": video_id})
    if result.get("status") == "success":
        await update.message.reply_text(f"▶️ Playing YouTube video: {url}\n\n(Note: Playback starts in background)")
    else:
        await update.message.reply_text(f"❌ {result.get('message', str(result))}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    client = await get_opencode()
    
    health = await client.health_check()
    if not health:
        await update.message.reply_text(
            "⚠️ OpenCode server not running!\n\n"
            "Please start opencode first, then try again."
        )
        return
    
    if user_id not in user_sessions:
        await update.message.reply_text(
            "🤖 Starting a new chat session for you...",
            parse_mode="Markdown"
        )
        
        session = await client.create_session(title=f"Telegram User {user_id}")
        
        if "error" in session:
            await update.message.reply_text(f"Failed to create session: {session['error']}")
            return
        
        session_id = session.get("session_id")
        if not session_id:
            await update.message.reply_text(f"Failed: {session}")
            return
        
        user_sessions[user_id] = session_id
    
    session_id = user_sessions[user_id]
    
    await update.message.reply_text("🤔 Thinking...", parse_mode="Markdown")
    
    result = await client.send_prompt(session_id, text)
    
    if "error" in result:
        await update.message.reply_text(f"Error: {result['error']}")
    else:
        response = result.get("response", "No response")
        await update.message.reply_text(response)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("newchat", newchat_command))
    app.add_handler(CommandHandler("clearchat", clearchat_command))
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("speak", speak_command))
    app.add_handler(CommandHandler("sysinfo", sysinfo_command))
    app.add_handler(CommandHandler("volume", volume_command))
    app.add_handler(CommandHandler("brightness", brightness_command))
    app.add_handler(CommandHandler("open", open_command))
    app.add_handler(CommandHandler("darkmode", darkmode_command))
    app.add_handler(CommandHandler("power", power_command))
    app.add_handler(CommandHandler("lock", lock_command))
    app.add_handler(CommandHandler("screenshot", screenshot_command))
    app.add_handler(CommandHandler("kill", kill_command))
    app.add_handler(CommandHandler("wifi", wifi_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("chrome", chrome_command))
    app.add_handler(CommandHandler("navigate", navigate_command))
    app.add_handler(CommandHandler("click", click_command))
    app.add_handler(CommandHandler("type", type_command))
    app.add_handler(CommandHandler("gettext", gettext_command))
    app.add_handler(CommandHandler("title", pagetitle_command))
    app.add_handler(CommandHandler("screenshot", chrome_screenshot_command))
    app.add_handler(CommandHandler("closechrome", chromeclose_command))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Telegram bot starting...")
    print("📡 OpenCode integration enabled!")
    print("Send a message to @Open_codebot!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

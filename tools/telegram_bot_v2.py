#!/usr/bin/env python3
"""
Telegram Bot v2 - Integrated with OpenCode Autonomy System
Features: /goal, /do, background tasks, system monitoring, multi-agent coordination
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, CallbackQueryHandler
)

from utils import config, security_manager, task_queue
from agents.planner import planner
from multiagent.coordinator import coordinator
from nlp.task_parser import task_parser
from monitoring.daemon import monitoring_daemon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# User sessions storage
user_sessions = {}
pending_confirmations = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(str(chat_id), "/start")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    welcome_text = (
        "🤖 **OpenCode Autonomy Bot v2**\n\n"
        "✨ *Welcome to your AI-powered autonomous assistant!*\n\n"
        "🚀 **Quick Start:**\n"
        "• /goal <description> - Execute a complex goal\n"
        "• /do <task> - Execute a natural language task\n"
        "• /run <command> - Run shell commands\n"
        "• /sysinfo - Check system status\n"
        "• /newchat - Start new AI chat session\n"
        "• /help - Show all commands\n\n"
        "💡 *Just send a message to chat with AI!*"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 **OpenCode Autonomy Bot v2**\n\n"
        "✨ *Your AI-powered autonomous assistant!*\n\n"
        "🎯 **Goal Execution:**\n"
        "• /goal <description> - Execute complex goals with multi-agent system\n"
        "• /do <task> - Execute natural language tasks\n\n"
        "⚙️ **System Control:**\n"
        "• /run <command> - Run shell commands\n"
        "• /sysinfo - Check system status (CPU, RAM, Disk)\n"
        "• /volume <0-100> - Set system volume\n"
        "• /brightness <0-100> - Set screen brightness\n\n"
        "💬 **Chat Management:**\n"
        "• /newchat - Start new AI session\n"
        "• /clearchat - Clear current session\n\n"
        "📝 **Examples:**\n"
        "• /goal Open browser and search for Python tutorials\n"
        "• /do Take a screenshot of the current page\n"
        "• /run ls -la\n\n"
        "🔮 *Just send a message to chat with AI!*"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def goal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /goal command - Execute a complex goal"""
    chat_id = str(update.effective_chat.id)
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(chat_id, "/goal")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /goal <description>\nExample: /goal Open browser and search for Python")
        return
    
    goal = " ".join(context.args)
    
    # Send confirmation if required
    if security_manager.requires_confirmation(goal):
        await request_confirmation(update, goal, "goal")
        return
    
    # Execute goal using multi-agent system
    await update.message.reply_text(f"ðŸ”„ Executing goal: {goal}")
    
    try:
        result = await coordinator.execute_goal(goal, user_id=chat_id)
        
        if result["status"] == "completed":
            success_msg = (
                f"âœ… Goal completed successfully!\n\n"
                f"**Goal:** {goal}\n"
                f"**Steps:** {result.get('steps_completed', 0)}/{result.get('total_steps', 0)}\n"
                f"**Time:** {result.get('duration', 0):.2f}s"
            )
            await update.message.reply_text(success_msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"âš ï¸ Goal partially completed: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Error executing goal: {e}")
        await update.message.reply_text(f"âŒ Error executing goal: {str(e)}")


async def do_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /do command - Execute natural language task"""
    chat_id = str(update.effective_chat.id)
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(chat_id, "/do")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /do <task>\nExample: /do Take a screenshot")
        return
    
    task = " ".join(context.args)
    
    # Parse natural language into tool calls
    await update.message.reply_text(f"ðŸ¤” Parsing task: {task}")
    
    try:
        tool_calls = await task_parser.parse(task)
        
        if not tool_calls:
            await update.message.reply_text("âŒ Could not parse task")
            return
        
        # Execute each tool call
        results = []
        for i, tool_call in enumerate(tool_calls, 1):
            await update.message.reply_text(f"Step {i}/{len(tool_calls)}: {tool_call['description']}")
            
            # Execute tool (simplified - in production, use actual tool execution)
            result = await execute_tool_call(tool_call)
            results.append(result)
            
            if result.get("status") != "success":
                await update.message.reply_text(f"âš ï¸ Step {i} failed: {result.get('message', '')}")
                break
        
        # Summary
        success_count = sum(1 for r in results if r.get("status") == "success")
        await update.message.reply_text(
            f"âœ… Task completed: {success_count}/{len(tool_calls)} steps successful"
        )
    
    except Exception as e:
        logger.error(f"Error executing /do command: {e}")
        await update.message.reply_text(f"âŒ Error: {str(e)}")


async def execute_tool_call(tool_call: dict) -> dict:
    """Execute a single tool call (placeholder implementation)"""
    tool = tool_call["tool"]
    params = tool_call.get("params", {})
    
    try:
        if tool == "run_command":
            import subprocess
            command = params.get("command", "")
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr
            }
        
        elif tool == "check_system":
            import psutil
            return {
                "status": "success",
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent
            }
        
        else:
            # Placeholder for other tools
            return {"status": "success", "message": f"Tool {tool} executed (placeholder)"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /run command - Run shell command"""
    chat_id = str(update.effective_chat.id)
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(chat_id, "/run")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return
    
    command = " ".join(context.args)
    
    # Check if command requires confirmation
    if security_manager.requires_confirmation(command):
        await request_confirmation(update, command, "run")
        return
    
    # Execute command
    await update.message.reply_text(f"âš™ï¸ Running: `{command}`", parse_mode="Markdown")
    
    try:
        import subprocess
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "Command executed successfully (no output)"
        
        # Truncate if too long
        if len(output) > 4000:
            output = output[:4000] + "\n\n[Output truncated...]"
        
        await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
        
        # Audit log
        security_manager.audit_log(chat_id, command, result.returncode == 0, "Command executed")
    
    except subprocess.TimeoutExpired:
        await update.message.reply_text("âŒ Command timed out")
    except Exception as e:
        logger.error(f"Error running command: {e}")
        await update.message.reply_text(f"âŒ Error: {str(e)}")


async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sysinfo command"""
    chat_id = str(update.effective_chat.id)
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(chat_id, "/sysinfo")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    try:
        import psutil
        
        # Collect metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Format message
        message = (
            f"ðŸ“Š **System Information**\n\n"
            f"**CPU:** {cpu_percent}%\n"
            f"**Memory:** {memory.percent}% ({memory.available / (1024**3):.1f} GB free)\n"
            f"**Disk:** {disk.percent}% ({disk.free / (1024**3):.1f} GB free)\n"
            f"**Python:** {sys.version.split()[0]}"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        await update.message.reply_text(f"âŒ Error: {str(e)}")


async def request_confirmation(update: Update, command: str, command_type: str):
    """Request user confirmation for dangerous commands"""
    chat_id = str(update.effective_chat.id)
    command_id = f"{chat_id}_{command_type}_{asyncio.get_event_loop().time()}"
    
    # Store pending confirmation
    pending_confirmations[command_id] = {
        "chat_id": chat_id,
        "command": command,
        "type": command_type,
        "update": update,
        "confirmed": False
    }
    
    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("âœ… Confirm", callback_data=f"confirm_{command_id}"),
            InlineKeyboardButton("âŒ Cancel", callback_data=f"cancel_{command_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"âš ï¸ **Confirmation Required**\n\n"
        f"Command: `{command}`\n\n"
        f"This command requires confirmation. Do you want to proceed?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    command_id = data.split("_", 1)[1]
    
    if command_id not in pending_confirmations:
        await query.edit_message_text("âŒ Confirmation expired or invalid")
        return
    
    pending = pending_confirmations[command_id]
    
    if data.startswith("confirm_"):
        # User confirmed
        pending["confirmed"] = True
        del pending_confirmations[command_id]
        
        await query.edit_message_text("âœ… Command confirmed. Executing...")
        
        # Execute the command
        if pending["type"] == "run":
            # Re-run the command
            context.args = pending["command"].split()
            await run_command(pending["update"], context)
        
        elif pending["type"] == "goal":
            # Re-run the goal
            context.args = pending["command"].split()
            await goal_command(pending["update"], context)
    
    elif data.startswith("cancel_"):
        # User cancelled
        del pending_confirmations[command_id]
        await query.edit_message_text("âŒ Command cancelled")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages - chat with AI"""
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    
    # Security check
    allowed, reason = security_manager.is_command_allowed(chat_id, "message")
    if not allowed:
        await update.message.reply_text(f"âŒ Access denied: {reason}")
        return
    
    # Use OpenCode client to chat
    client = OpenCodeClient()
    
    try:
        # Get or create session
        if chat_id not in user_sessions:
            session = await client.create_session(title=f"Telegram User {chat_id}")
            if "error" in session:
                await update.message.reply_text(f"âŒ Failed to create session: {session['error']}")
                return
            user_sessions[chat_id] = session.get("session_id")
        
        session_id = user_sessions[chat_id]
        
        # Send message to AI
        await update.message.reply_text("ðŸ¤” Thinking...", parse_mode="Markdown")
        
        result = await client.send_prompt(session_id, text)
        
        if "error" in result:
            await update.message.reply_text(f"âŒ Error: {result['error']}")
        else:
            response = result.get("response", "No response")
            await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(f"âŒ Error: {str(e)}")


# OpenCode client class (simplified version)
class OpenCodeClient:
    def __init__(self, base_url: str = "http://localhost:4096"):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def create_session(self, title: str = "Telegram Chat"):
        try:
            async with self.session.post(
                f"{self.base_url}/session",
                json={"title": title, "directory": config.WORKSPACE_PATH}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"session_id": data.get("id"), "data": data}
                return {"error": f"Failed: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_prompt(self, session_id: str, text: str):
        try:
            payload = {
                "parts": [{"type": "text", "text": text}],
                "directory": config.WORKSPACE_PATH
            }
            async with self.session.post(
                f"{self.base_url}/session/{session_id}/message",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._extract_response(data)
                return {"error": f"Request failed: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_response(self, data: dict) -> dict:
        parts = data.get("parts", [])
        if not parts:
            parts = data.get("data", {}).get("parts", [])
        
        text_parts = []
        for part in parts:
            if part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        
        full_text = "\n".join(text_parts)
        if len(full_text) > 4000:
            full_text = full_text[:4000] + "\n\n[Response truncated...]"
        
        return {"response": full_text}


def main():
    """Main entry point"""
    # Validate configuration
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # Create application
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("goal", goal_command))
    app.add_handler(CommandHandler("do", do_command))
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("sysinfo", sysinfo_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start monitoring daemon in background
    async def start_monitoring():
        asyncio.create_task(monitoring_daemon.start(check_interval=300))
    
    # Initialize task queue
    async def init_task_queue():
        await task_queue.initialize()
    
    print("ðŸ¤– OpenCode Autonomy Bot v2 starting...")
    print(f"ðŸ“¡ Monitoring: http://localhost:4096")
    print(f"ðŸ”’ Allowed chats: {'All' if not config.ALLOWED_CHAT_IDS else config.ALLOWED_CHAT_IDS}")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

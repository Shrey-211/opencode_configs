"""
Security module for OpenCode Autonomy System
Handles command confirmation, chat ID validation, and audit logging
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from .config_loader import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security aspects of the system"""
    
    def __init__(self):
        self.pending_confirmations = {}  # chat_id -> {command_id: command}
    
    def is_command_allowed(self, chat_id: str, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if a command is allowed for a chat ID
        
        Returns:
            (is_allowed, reason_if_denied)
        """
        # Check chat ID whitelist
        if not config.is_allowed_chat(chat_id):
            return False, "Chat ID not in allowed list"
        
        # Check if command requires confirmation
        if config.requires_confirmation(command):
            return False, "Command requires confirmation"
        
        return True, None
    
    def requires_confirmation(self, command: str) -> bool:
        """
        Check if a command requires confirmation
        
        Returns:
            True if command requires confirmation
        """
        return config.requires_confirmation(command)
    
    async def request_confirmation(self, chat_id: str, command: str, command_id: str) -> bool:
        """
        Request confirmation for a dangerous command
        
        Returns:
            True if confirmed, False otherwise
        """
        # Store pending confirmation
        if chat_id not in self.pending_confirmations:
            self.pending_confirmations[chat_id] = {}
        
        self.pending_confirmations[chat_id][command_id] = {
            'command': command,
            'timestamp': datetime.now(),
            'confirmed': False
        }
        
        logger.info(f"Confirmation requested for command: {command} (chat: {chat_id})")
        
        # Wait for confirmation (with timeout)
        try:
            await asyncio.wait_for(
                self._wait_for_confirmation(chat_id, command_id),
                timeout=60.0  # 60 second timeout
            )
            return True
        except asyncio.TimeoutError:
            # Clean up expired confirmation
            if chat_id in self.pending_confirmations:
                self.pending_confirmations[chat_id].pop(command_id, None)
            return False
    
    async def _wait_for_confirmation(self, chat_id: str, command_id: str):
        """Wait for user to confirm the command"""
        while True:
            if chat_id in self.pending_confirmations:
                cmd_data = self.pending_confirmations[chat_id].get(command_id)
                if cmd_data and cmd_data.get('confirmed'):
                    return True
            await asyncio.sleep(0.1)
    
    def confirm_command(self, chat_id: str, command_id: str) -> bool:
        """
        Mark a command as confirmed by the user
        
        Returns:
            True if command was found and confirmed
        """
        if chat_id in self.pending_confirmations:
            if command_id in self.pending_confirmations[chat_id]:
                self.pending_confirmations[chat_id][command_id]['confirmed'] = True
                logger.info(f"Command confirmed: {command_id} (chat: {chat_id})")
                return True
        return False
    
    def cancel_confirmation(self, chat_id: str, command_id: str) -> bool:
        """
        Cancel a pending confirmation
        
        Returns:
            True if confirmation was cancelled
        """
        if chat_id in self.pending_confirmations:
            if command_id in self.pending_confirmations[chat_id]:
                del self.pending_confirmations[chat_id][command_id]
                logger.info(f"Confirmation cancelled: {command_id} (chat: {chat_id})")
                return True
        return False
    
    def audit_log(self, chat_id: str, command: str, success: bool, details: str = ""):
        """Log command execution for audit purposes"""
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"{timestamp} | Chat: {chat_id} | Command: {command} | Status: {status} | Details: {details}"
        
        logger.info(log_entry)
        
        # Optionally write to file
        try:
            with open("audit_log.txt", "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")


# Global security manager instance
security_manager = SecurityManager()


def requires_confirmation_decorator(func):
    """
    Decorator to require confirmation for dangerous commands
    """
    async def wrapper(*args, **kwargs):
        # Extract chat_id and command from function arguments
        # This is a simplified approach - adjust based on your function signatures
        chat_id = kwargs.get('chat_id') or (args[0] if args else None)
        command = kwargs.get('command') or (args[1] if len(args) > 1 else None)
        
        if chat_id and command and config.requires_confirmation(command):
            command_id = f"{chat_id}_{datetime.now().timestamp()}"
            
            # Request confirmation
            confirmed = await security_manager.request_confirmation(chat_id, command, command_id)
            
            if not confirmed:
                raise PermissionError(f"Command '{command}' requires confirmation but was not confirmed")
        
        return await func(*args, **kwargs)
    
    return wrapper


if __name__ == "__main__":
    # Test security manager
    sm = SecurityManager()
    
    # Test chat ID validation
    allowed, reason = sm.is_command_allowed("123456789", "echo test")
    print(f"Test 1 - Allowed: {allowed}, Reason: {reason}")
    
    # Test dangerous command detection
    allowed, reason = sm.is_command_allowed("123456789", "shutdown now")
    print(f"Test 2 - Allowed: {allowed}, Reason: {reason}")

"""
Configuration loader for OpenCode Autonomy System
Loads environment variables and provides configuration access
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Main configuration class"""
    
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ALLOWED_CHAT_IDS = os.getenv("ALLOWED_CHAT_IDS", "").split(",") if os.getenv("ALLOWED_CHAT_IDS") else []
    
    # AI API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # System Monitoring Thresholds
    CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", 90))
    RAM_THRESHOLD = int(os.getenv("RAM_THRESHOLD", 85))
    DISK_THRESHOLD = int(os.getenv("DISK_THRESHOLD", 90))
    
    # Confirmation Settings
    REQUIRE_CONFIRMATION = os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true"
    DANGEROUS_COMMANDS = os.getenv("DANGEROUS_COMMANDS", "shutdown,restart,kill,rm,format,mkfs").split(",")
    
    # Directory Paths
    WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "D:/workspace/open_code")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "D:/workspace/open_code/screenshots")
    
    @classmethod
    def is_allowed_chat(cls, chat_id: str) -> bool:
        """Check if chat ID is allowed"""
        if not cls.ALLOWED_CHAT_IDS:
            return True  # Empty list means allow all
        return str(chat_id) in cls.ALLOWED_CHAT_IDS
    
    @classmethod
    def requires_confirmation(cls, command: str) -> bool:
        """Check if command requires user confirmation"""
        if not cls.REQUIRE_CONFIRMATION:
            return False
        
        command_lower = command.lower()
        return any(dc in command_lower for dc in cls.DANGEROUS_COMMANDS)
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis connection URL"""
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN not set in .env file")
        
        if cls.REQUIRE_CONFIRMATION and not cls.DANGEROUS_COMMANDS:
            errors.append("DANGEROUS_COMMANDS not configured")
        
        return errors

# Global config instance
config = Config()

if __name__ == "__main__":
    # Test configuration
    errors = Config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid")
        print(f"Redis URL: {Config.get_redis_url()}")
        print(f"Allowed chats: {Config.ALLOWED_CHAT_IDS or 'All'}")

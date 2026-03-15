"""
Natural Language Task Parser
Converts natural language task descriptions into structured tool calls
"""
import asyncio
import json
import logging
import re
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskParser:
    """Parses natural language tasks into structured tool calls"""
    
    def __init__(self):
        self.available_tools = [
            {
                "name": "open_browser",
                "description": "Open a web browser and navigate to a URL",
                "examples": ["open google.com", "go to github.com", "visit website"]
            },
            {
                "name": "click",
                "description": "Click on an element",
                "examples": ["click button", "click link", "click submit"]
            },
            {
                "name": "type",
                "description": "Type text into an input field",
                "examples": ["type hello in search box", "enter username"]
            },
            {
                "name": "get_text",
                "description": "Extract text from a page element",
                "examples": ["get text from heading", "read the title"]
            },
            {
                "name": "screenshot",
                "description": "Take a screenshot",
                "examples": ["take screenshot", "capture screen"]
            },
            {
                "name": "run_command",
                "description": "Execute a shell command",
                "examples": ["run ls", "execute git status", "run command"]
            },
            {
                "name": "check_system",
                "description": "Check system status",
                "examples": ["check system", "show system info", "check resources"]
            }
        ]
    
    async def parse(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Parse natural language task into structured tool calls
        
        Args:
            task_description: Natural language task description
        
        Returns:
            List of tool call dictionaries
        """
        logger.info(f"Parsing task: {task_description}")
        
        # Simple rule-based parsing for now
        # In production, this would use an LLM for better understanding
        tool_calls = self._rule_based_parse(task_description)
        
        logger.info(f"Parsed into {len(tool_calls)} tool calls")
        return tool_calls
    
    def _rule_based_parse(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Simple rule-based parsing
        """
        task_lower = task_description.lower()
        tool_calls = []
        
        # Extract URLs
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, task_description)
        
        # Browser actions
        if any(word in task_lower for word in ["open", "go to", "visit", "navigate"]):
            url = urls[0] if urls else "https://www.google.com"
            tool_calls.append({
                "tool": "open_browser",
                "params": {"url": url},
                "description": f"Open browser and navigate to {url}"
            })
        
        # Click actions
        if "click" in task_lower:
            # Try to extract what to click
            click_target = self._extract_click_target(task_description)
            tool_calls.append({
                "tool": "click",
                "params": {"selector": click_target},
                "description": f"Click on {click_target}"
            })
        
        # Type actions
        if any(word in task_lower for word in ["type", "enter", "input"]):
            text_match = re.search(r'type\s+["\']?([^"\']+)["\']?', task_lower)
            if text_match:
                text = text_match.group(1)
                # Try to find where to type (selector)
                selector = "input, textarea"  # Default
                tool_calls.append({
                    "tool": "type",
                    "params": {"selector": selector, "text": text},
                    "description": f"Type '{text}' into {selector}"
                })
        
        # Screenshot actions
        if any(word in task_lower for word in ["screenshot", "capture", "screen shot"]):
            tool_calls.append({
                "tool": "screenshot",
                "params": {},
                "description": "Take screenshot"
            })
        
        # System check actions
        if any(word in task_lower for word in ["system", "check system", "resources"]):
            tool_calls.append({
                "tool": "check_system",
                "params": {},
                "description": "Check system status"
            })
        
        # Command execution
        if any(word in task_lower for word in ["run", "execute", "command"]):
            # Extract command
            command_match = re.search(r'run\s+(.+)', task_lower)
            if command_match:
                command = command_match.group(1)
                tool_calls.append({
                    "tool": "run_command",
                    "params": {"command": command},
                    "description": f"Run command: {command}"
                })
        
        # Default: if no tools matched, try to extract intent
        if not tool_calls:
            tool_calls.append({
                "tool": "run_command",
                "params": {"command": f'echo "Task: {task_description}"'},
                "description": f"Acknowledge task: {task_description}"
            })
        
        return tool_calls
    
    def _extract_click_target(self, task_description: str) -> str:
        """
        Extract what element to click from task description
        """
        task_lower = task_description.lower()
        
        # Common click targets
        if "button" in task_lower:
            return "button"
        elif "link" in task_lower:
            return "a"
        elif "submit" in task_lower:
            return "button[type='submit'], input[type='submit']"
        elif "search" in task_lower:
            return "input[type='search'], .search"
        else:
            return "button, a, input[type='button']"


# Global task parser instance
task_parser = TaskParser()


if __name__ == "__main__":
    # Test the parser
    async def test():
        tasks = [
            "Open google.com and search for python",
            "Click the submit button",
            "Type hello world in the search box",
            "Take a screenshot of the page",
            "Check system resources",
            "Run ls -la command"
        ]
        
        for task in tasks:
            print(f"\nTask: {task}")
            tool_calls = await task_parser.parse(task)
            print(f"Tool calls: {json.dumps(tool_calls, indent=2)}")
    
    asyncio.run(test())

"""
Executor Agent for Goal-Driven Task Execution
Executes planned steps using available tools
"""
import asyncio
import logging
from typing import Dict, Any, Optional

import importlib.util
import sys
import os

# Dynamically import selenium_tool from tools directory
tools_path = os.path.join(os.path.dirname(__file__), '..', 'tools', 'selenium_tool.py')
spec = importlib.util.spec_from_file_location("selenium_tool", tools_path)

if spec is not None and spec.loader is not None:
    selenium_module = importlib.util.module_from_spec(spec)
    sys.modules["selenium_tool"] = selenium_module
    spec.loader.exec_module(selenium_module)
    
    # Import functions from the module
    open_chrome = selenium_module.open_chrome
    navigate = selenium_module.navigate
    click = selenium_module.click
    type_text = selenium_module.type_text
    get_text = selenium_module.get_text
    screenshot = selenium_module.screenshot
    close_browser = selenium_module.close_browser
else:
    raise ImportError(f"Could not load selenium_tool from {tools_path}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutorAgent:
    """Agent responsible for executing planned steps"""
    
    def __init__(self):
        self.browser_open = False
    
    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step from a plan
        
        Args:
            step: Step dictionary with action and params
        
        Returns:
            Execution result
        """
        action = step.get("action")
        params = step.get("params", {})
        
        logger.info(f"Executing step: {action} with params: {params}")
        
        try:
            if action == "open_browser":
                url = params.get("url", "https://www.google.com")
                result = await open_chrome(url)
                self.browser_open = True
                return result
            
            elif action == "navigate":
                url = params.get("url")
                if url:
                    result = await navigate(url)
                    return result
                return {"status": "error", "message": "No URL provided"}
            
            elif action == "click":
                selector = params.get("selector")
                if selector:
                    result = await click(selector)
                    return result
                return {"status": "error", "message": "No selector provided"}
            
            elif action == "type":
                selector = params.get("selector")
                text = params.get("text")
                if selector and text:
                    result = await type_text(selector, text)
                    return result
                return {"status": "error", "message": "Missing selector or text"}
            
            elif action == "get_text":
                selector = params.get("selector", "body")
                result = await get_text(selector)
                return result
            
            elif action == "screenshot":
                result = await screenshot()
                return result
            
            elif action == "run_command":
                command = params.get("command")
                if command:
                    # Import subprocess to run commands
                    import subprocess
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        capture_output=True, 
                        text=True
                    )
                    return {
                        "status": "success" if result.returncode == 0 else "error",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                return {"status": "error", "message": "No command provided"}
            
            elif action == "check_system":
                import psutil
                return {
                    "status": "success",
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                }
            
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Error executing step {action}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all steps in a plan
        
        Args:
            plan: Plan dictionary with steps
        
        Returns:
            Execution results for all steps
        """
        results = []
        
        for i, step in enumerate(plan.get("steps", [])):
            logger.info(f"Executing step {i+1}/{len(plan['steps'])}")
            
            result = await self.execute_step(step)
            results.append({
                "step_index": i,
                "step": step,
                "result": result
            })
            
            # Stop if a step fails (unless it's non-critical)
            if result.get("status") == "error" and step.get("critical", True):
                logger.error(f"Critical step failed: {step.get('action')}")
                break
        
        # Clean up if browser was opened
        if self.browser_open:
            await close_browser()
            self.browser_open = False
        
        return {
            "status": "completed" if all(r["result"].get("status") == "success" for r in results) else "partial",
            "results": results
        }


# Global executor instance
executor = ExecutorAgent()


if __name__ == "__main__":
    # Test the executor
    async def test():
        # Test simple step execution
        step = {
            "action": "run_command",
            "params": {"command": "echo 'Hello from Executor Agent'"}
        }
        
        result = await executor.execute_step(step)
        print(f"Step result: {result}")
    
    asyncio.run(test())

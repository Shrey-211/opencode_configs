"""
Planner Agent for Goal-Driven Task Breakdown
Converts natural language goals into structured execution plans
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional

from utils import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for breaking down goals into executable steps"""
    
    def __init__(self):
        self.available_actions = [
            {
                "name": "open_browser",
                "description": "Open a web browser and navigate to a URL",
                "params": {"url": "URL to navigate to"}
            },
            {
                "name": "click",
                "description": "Click on an element using CSS selector",
                "params": {"selector": "CSS selector for the element"}
            },
            {
                "name": "type",
                "description": "Type text into an input field",
                "params": {"selector": "CSS selector", "text": "Text to type"}
            },
            {
                "name": "get_text",
                "description": "Extract text from an element",
                "params": {"selector": "CSS selector"}
            },
            {
                "name": "screenshot",
                "description": "Take a screenshot of the current page",
                "params": {}
            },
            {
                "name": "run_command",
                "description": "Run a shell command",
                "params": {"command": "Command to execute"}
            },
            {
                "name": "check_system",
                "description": "Check system status (CPU, RAM, Disk)",
                "params": {}
            }
        ]
    
    async def create_plan(self, goal: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an execution plan for a goal
        
        Args:
            goal: Natural language goal description
            user_id: Optional user ID for context
        
        Returns:
            Plan dictionary with steps and metadata
        """
        logger.info(f"Creating plan for goal: {goal}")
        
        # Use OpenCode AI to generate the plan
        plan = await self._generate_plan_with_ai(goal)
        
        # Validate the plan
        validated_plan = self._validate_plan(plan)
        
        # Store plan in memory (if user_id provided)
        if user_id:
            await self._store_plan(user_id, validated_plan)
        
        logger.info(f"Generated plan with {len(validated_plan['steps'])} steps")
        return validated_plan
    
    async def _generate_plan_with_ai(self, goal: str) -> Dict[str, Any]:
        """
        Generate plan using OpenCode AI or direct API call
        """
        # Create a prompt for the AI
        prompt = f"""
        You are an expert AI assistant that breaks down goals into executable steps.
        
        Available actions:
        {json.dumps(self.available_actions, indent=2)}
        
        Goal: {goal}
        
        Create a step-by-step plan to achieve this goal.
        Return ONLY valid JSON with the following structure:
        {{
            "goal": "{goal}",
            "steps": [
                {{
                    "action": "action_name",
                    "params": {{}},
                    "description": "What this step does"
                }}
            ],
            "estimated_time": "X minutes",
            "complexity": "low/medium/high",
            "confidence": 0.0-1.0
        }}
        
        Steps should be specific and actionable.
        """
        
        # For now, use a simple rule-based approach
        # In production, this would call OpenCode or an LLM API
        plan = self._rule_based_planner(goal)
        
        return plan
    
    def _rule_based_planner(self, goal: str) -> Dict[str, Any]:
        """
        Simple rule-based planner for demonstration
        In production, replace with AI-powered planning
        """
        goal_lower = goal.lower()
        steps = []
        
        # Rule-based goal parsing
        if "browser" in goal_lower or "website" in goal_lower or "http" in goal_lower:
            # Extract URL if present
            import re
            url_match = re.search(r'(https?://[^\s]+)', goal)
            url = url_match.group(1) if url_match else "https://www.google.com"
            
            steps = [
                {
                    "action": "open_browser",
                    "params": {"url": url},
                    "description": f"Open browser and navigate to {url}"
                }
            ]
            
            # Add click/extract steps if goal mentions them
            if "click" in goal_lower:
                steps.append({
                    "action": "click",
                    "params": {"selector": "button, a, .clickable"},
                    "description": "Click on the target element"
                })
            
            if "extract" in goal_lower or "get" in goal_lower:
                steps.append({
                    "action": "get_text",
                    "params": {"selector": "body"},
                    "description": "Extract text content"
                })
            
            steps.append({
                "action": "screenshot",
                "params": {},
                "description": "Take screenshot of results"
            })
        
        elif "system" in goal_lower or "check" in goal_lower:
            steps = [
                {
                    "action": "check_system",
                    "params": {},
                    "description": "Check system status"
                }
            ]
        
        elif "run" in goal_lower or "command" in goal_lower:
            # Extract command if present
            import re
            command_match = re.search(r'run\s+(.+)', goal_lower)
            command = command_match.group(1) if command_match else "echo 'Hello World'"
            
            steps = [
                {
                    "action": "run_command",
                    "params": {"command": command},
                    "description": f"Run command: {command}"
                }
            ]
        
        else:
            # Default plan for unknown goals
            steps = [
                {
                    "action": "run_command",
                    "params": {"command": f'echo "Goal: {goal}"'},
                    "description": "Acknowledge goal"
                }
            ]
        
        return {
            "goal": goal,
            "steps": steps,
            "estimated_time": f"{len(steps) * 2} minutes",
            "complexity": "medium" if len(steps) > 3 else "low",
            "confidence": 0.7
        }
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan structure and parameters"""
        validated = plan.copy()
        
        # Ensure required fields exist
        if "steps" not in validated:
            validated["steps"] = []
        
        # Validate each step
        validated_steps = []
        for step in validated["steps"]:
            if "action" not in step:
                continue
            
            # Ensure params exists
            if "params" not in step:
                step["params"] = {}
            
            validated_steps.append(step)
        
        validated["steps"] = validated_steps
        
        # Set defaults
        validated.setdefault("estimated_time", "Unknown")
        validated.setdefault("complexity", "medium")
        validated.setdefault("confidence", 0.5)
        
        return validated
    
    async def _store_plan(self, user_id: str, plan: Dict[str, Any]):
        """Store plan in memory (placeholder for Memory MCP integration)"""
        # This would integrate with Memory MCP in the future
        # For now, just log it
        logger.info(f"Stored plan for user {user_id}: {plan['goal']}")


# Global planner instance
planner = PlannerAgent()


if __name__ == "__main__":
    # Test the planner
    async def test():
        # Test different goal types
        goals = [
            "Open browser and go to GitHub",
            "Check my system status",
            "Run a command to list files",
            "Extract text from a website"
        ]
        
        for goal in goals:
            print(f"\nGoal: {goal}")
            plan = await planner.create_plan(goal)
            print(f"Plan: {json.dumps(plan, indent=2)}")
    
    asyncio.run(test())

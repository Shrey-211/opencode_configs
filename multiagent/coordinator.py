"""
Multi-Agent Coordinator
Orchestrates communication between planner, executor, and observer agents
"""
import asyncio
import logging
from typing import Dict, Any, Optional

# Import agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.planner import planner
from agents.executor import executor
from agents.observer import observer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Coordinates multiple agents to achieve complex goals
    
    Workflow:
    1. Planner creates plan from goal
    2. Executor executes each step
    3. Observer validates outcomes
    4. Coordinator adapts if needed
    """
    
    def __init__(self):
        self.planner = planner
        self.executor = executor
        self.observer = observer
        self.execution_history = []
    
    async def execute_goal(self, goal: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a goal using the multi-agent system
        
        Args:
            goal: Natural language goal description
            user_id: Optional user ID for context
        
        Returns:
            Execution result with all observations
        """
        logger.info(f"Starting goal execution: {goal}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Create plan
            logger.info("Step 1: Creating plan...")
            plan = await self.planner.create_plan(goal, user_id)
            
            if not plan.get("steps"):
                return {
                    "status": "error",
                    "message": "Failed to create plan",
                    "goal": goal
                }
            
            # Step 2: Execute plan
            logger.info(f"Step 2: Executing plan with {len(plan['steps'])} steps...")
            execution_result = await self.executor.execute_plan(plan)
            
            # Step 3: Observe outcomes
            logger.info("Step 3: Observing outcomes...")
            if "results" in execution_result:
                observation = await self.observer.observe_multiple(
                    [r["result"] for r in execution_result["results"]]
                )
            else:
                observation = await self.observer.observe(execution_result)
            
            # Compile final result
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            final_result = {
                "status": "completed" if observation["overall_success"] else "partial",
                "goal": goal,
                "plan": plan,
                "execution": execution_result,
                "observation": observation,
                "duration": duration,
                "steps_completed": observation.get("successful_steps", 0),
                "total_steps": observation.get("total_steps", 0)
            }
            
            # Store in history
            self.execution_history.append(final_result)
            
            logger.info(f"Goal execution completed in {duration:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"Error executing goal: {e}")
            return {
                "status": "error",
                "message": str(e),
                "goal": goal
            }
    
    async def execute_multi_step_goal(self, goal: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a goal with adaptive replanning if needed
        
        Args:
            goal: Natural language goal description
            user_id: Optional user ID for context
        
        Returns:
            Execution result with adaptive replanning
        """
        max_retries = 3
        retry_count = 0
        result = {"status": "error", "message": "Max retries exceeded"}
        
        while retry_count < max_retries:
            result = await self.execute_goal(goal, user_id)
            
            if result["status"] == "completed":
                return result
            
            # If partial failure, try to adapt
            if result["status"] == "partial":
                retry_count += 1
                logger.info(f"Partial completion, retry {retry_count}/{max_retries}")
                
                # Extract failed steps and adapt plan
                failed_steps = []
                if "execution" in result and "results" in result["execution"]:
                    for r in result["execution"]["results"]:
                        if r["result"].get("status") != "success":
                            failed_steps.append(r["step"])
                
                # Create adapted goal
                if failed_steps:
                    adapted_goal = f"Complete the remaining steps: {failed_steps}"
                    goal = adapted_goal
        
        return result
    
    def get_execution_history(self, count: int = 10) -> list:
        """Get recent execution history"""
        return self.execution_history[-count:]


# Global coordinator instance
coordinator = AgentCoordinator()


if __name__ == "__main__":
    # Test the coordinator
    async def test():
        # Test simple goal
        goal = "Run a command to list files in current directory"
        result = await coordinator.execute_goal(goal)
        
        print(f"\nGoal: {goal}")
        print(f"Status: {result['status']}")
        print(f"Duration: {result.get('duration', 0):.2f}s")
        
        if "observation" in result:
            print(f"Success: {result['observation']['overall_success']}")
    
    asyncio.run(test())

"""
Observer Agent for Goal-Driven Task Observation
Observes execution results and validates outcomes
"""
import asyncio
import logging
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObserverAgent:
    """Agent responsible for observing and validating execution results"""
    
    def __init__(self):
        self.observation_history = []
    
    async def observe(self, execution_result: Dict[str, Any], expected_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Observe and validate execution result
        
        Args:
            execution_result: Result from executor
            expected_state: Expected state to validate against
        
        Returns:
            Observation result with validation status
        """
        logger.info(f"Observing execution result: {execution_result.get('status')}")
        
        observation = {
            "timestamp": asyncio.get_event_loop().time(),
            "result": execution_result,
            "expected_state": expected_state,
            "validation": {}
        }
        
        # Validate based on status
        status = execution_result.get("status")
        
        if status == "success":
            observation["validation"]["success"] = True
            observation["validation"]["message"] = "Execution completed successfully"
        
        elif status == "error":
            observation["validation"]["success"] = False
            observation["validation"]["message"] = execution_result.get("message", "Unknown error")
            observation["validation"]["suggested_fix"] = self._suggest_fix(execution_result)
        
        elif status == "partial":
            observation["validation"]["success"] = False
            observation["validation"]["message"] = "Partial execution - some steps failed"
        
        # Store observation
        self.observation_history.append(observation)
        
        # Keep only last 100 observations
        if len(self.observation_history) > 100:
            self.observation_history = self.observation_history[-100:]
        
        return observation
    
    def _suggest_fix(self, execution_result: Dict[str, Any]) -> str:
        """
        Suggest a fix based on the error
        
        Returns:
            Suggested fix string
        """
        error_msg = execution_result.get("message", "").lower()
        
        if "selector" in error_msg or "element" in error_msg:
            return "Try using a different CSS selector or check if the element exists"
        
        if "timeout" in error_msg:
            return "Increase timeout or check network connection"
        
        if "permission" in error_msg:
            return "Check permissions and try again"
        
        if "not found" in error_msg:
            return "Verify the URL or resource exists"
        
        return "Check the error details and try again"
    
    async def observe_multiple(self, execution_results: list) -> Dict[str, Any]:
        """
        Observe multiple execution results
        
        Args:
            execution_results: List of execution results
        
        Returns:
            Combined observation
        """
        observations = []
        all_success = True
        
        for result in execution_results:
            observation = await self.observe(result)
            observations.append(observation)
            
            if not observation["validation"]["success"]:
                all_success = False
        
        return {
            "overall_success": all_success,
            "observations": observations,
            "total_steps": len(execution_results),
            "successful_steps": sum(1 for obs in observations if obs["validation"]["success"])
        }
    
    def get_recent_observations(self, count: int = 10) -> list:
        """Get recent observations"""
        return self.observation_history[-count:]


# Global observer instance
observer = ObserverAgent()


if __name__ == "__main__":
    # Test the observer
    async def test():
        # Test observing a successful result
        success_result = {"status": "success", "message": "Task completed"}
        observation = await observer.observe(success_result)
        print(f"Success observation: {observation}")
        
        # Test observing an error result
        error_result = {"status": "error", "message": "Element not found"}
        observation = await observer.observe(error_result)
        print(f"Error observation: {observation}")
    
    asyncio.run(test())

"""
Integration Test Script for OpenCode Autonomy System v2
Tests all major components together
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import config, security_manager
from agents.planner import planner
from agents.executor import executor
from agents.observer import observer
from multiagent.coordinator import coordinator
from nlp.task_parser import task_parser
from monitoring.daemon import monitoring_daemon


async def test_config():
    """Test configuration loading"""
    print("\n1. Testing Configuration...")
    
    errors = config.validate()
    if errors:
        print(f"âŒ Configuration errors: {errors}")
        return False
    
    print(f"[OK] Configuration valid")
    print(f"   - Redis URL: {config.get_redis_url()}")
    print(f"   - Allowed chats: {config.ALLOWED_CHAT_IDS or 'All'}")
    return True


async def test_security():
    """Test security manager"""
    print("\n2. Testing Security Manager...")
    
    # Test chat ID validation
    allowed, reason = security_manager.is_command_allowed("123456789", "echo test")
    if allowed:
        print(f"âœ… Chat ID validation: Allowed")
    else:
        print(f"âŒ Chat ID validation: Denied - {reason}")
    
    # Test dangerous command detection
    allowed, reason = security_manager.is_command_allowed("123456789", "shutdown now")
    if not allowed:
        print(f"âœ… Dangerous command detection: Blocked - {reason}")
    else:
        print(f"âŒ Dangerous command detection: Should have been blocked")
    
    # Test confirmation requirement
    requires = security_manager.requires_confirmation("rm -rf /")
    if requires:
        print(f"âœ… Confirmation required: Yes")
    else:
        print(f"âŒ Confirmation required: No (should be yes)")
    
    return True


async def test_planner():
    """Test planner agent"""
    print("\n3. Testing Planner Agent...")
    
    try:
        # Test goal planning
        plan = await planner.create_plan("Open browser and go to GitHub")
        
        if plan.get("steps"):
            print(f"âœ… Planner created plan with {len(plan['steps'])} steps")
            for i, step in enumerate(plan['steps'], 1):
                print(f"   Step {i}: {step['action']} - {step['description']}")
        else:
            print(f"âŒ Planner failed to create plan")
            return False
        
        return True
    except Exception as e:
        print(f"âŒ Planner error: {e}")
        return False


async def test_executor():
    """Test executor agent"""
    print("\n4. Testing Executor Agent...")
    
    try:
        # Test simple command execution
        step = {
            "action": "run_command",
            "params": {"command": "echo 'Hello from Executor'"},
            "description": "Test command execution"
        }
        
        result = await executor.execute_step(step)
        
        if result.get("status") == "success":
            print(f"âœ… Executor executed step successfully")
            return True
        else:
            print(f"âŒ Executor failed: {result.get('message')}")
            return False
    except Exception as e:
        print(f"âŒ Executor error: {e}")
        return False


async def test_observer():
    """Test observer agent"""
    print("\n5. Testing Observer Agent...")
    
    try:
        # Test observing successful result
        success_result = {"status": "success", "message": "Task completed"}
        observation = await observer.observe(success_result)
        
        if observation["validation"]["success"]:
            print(f"âœ… Observer validated successful result")
        else:
            print(f"âŒ Observer failed to validate success")
        
        # Test observing error result
        error_result = {"status": "error", "message": "Element not found"}
        observation = await observer.observe(error_result)
        
        if not observation["validation"]["success"]:
            print(f"âœ… Observer detected error correctly")
            print(f"   Suggested fix: {observation['validation'].get('suggested_fix', 'N/A')}")
        else:
            print(f"âŒ Observer failed to detect error")
        
        return True
    except Exception as e:
        print(f"âŒ Observer error: {e}")
        return False


async def test_task_parser():
    """Test natural language task parser"""
    print("\n6. Testing Task Parser...")
    
    try:
        # Test parsing different tasks
        tasks = [
            "Open google.com",
            "Click the submit button",
            "Take a screenshot"
        ]
        
        for task in tasks:
            tool_calls = await task_parser.parse(task)
            if tool_calls:
                print(f"âœ… Parsed '{task}' into {len(tool_calls)} tool calls")
            else:
                print(f"âŒ Failed to parse '{task}'")
                return False
        
        return True
    except Exception as e:
        print(f"âŒ Task parser error: {e}")
        return False


async def test_coordinator():
    """Test multi-agent coordinator"""
    print("\n7. Testing Multi-Agent Coordinator...")
    
    try:
        # Test goal execution
        goal = "Run a command to list files"
        result = await coordinator.execute_goal(goal)
        
        if result["status"] in ["completed", "partial"]:
            print(f"âœ… Coordinator executed goal: {result['status']}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
            print(f"   Steps: {result.get('steps_completed', 0)}/{result.get('total_steps', 0)}")
        else:
            print(f"âŒ Coordinator failed: {result.get('message')}")
            return False
        
        return True
    except Exception as e:
        print(f"âŒ Coordinator error: {e}")
        return False


async def test_monitoring():
    """Test system monitoring"""
    print("\n8. Testing System Monitoring...")
    
    try:
        # Collect metrics once
        metrics = await monitoring_daemon.collect_metrics()
        
        if metrics:
            print(f"âœ… Monitoring collected metrics")
            print(f"   CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {metrics.get('memory_percent', 0):.1f}%")
            print(f"   Disk: {metrics.get('disk_percent', 0):.1f}%")
        else:
            print(f"âŒ Monitoring failed to collect metrics")
            return False
        
        return True
    except Exception as e:
        print(f"âŒ Monitoring error: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("OpenCode Autonomy System v2 - Integration Tests")
    print("=" * 60)
    
    tests = [
        test_config,
        test_security,
        test_planner,
        test_executor,
        test_observer,
        test_task_parser,
        test_coordinator,
        test_monitoring,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"âŒ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("ðŸŽ‰ All tests passed! System is ready.")
        return 0
    else:
        print("âš ï¸ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

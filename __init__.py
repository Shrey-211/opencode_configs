"""
OpenCode Autonomy System v2
Goal-driven autonomous AI agent system built on OpenCode

Packages:
- utils: Configuration, security, task queue
- agents: Multi-agent system (planner, executor, observer)
- multiagent: Agent coordination
- nlp: Natural language processing
- monitoring: System monitoring
- tools: Telegram bot and other tools
- docs: Documentation
"""

from .utils import config, security_manager, task_queue

__version__ = "2.0.0"
__all__ = ['config', 'security_manager', 'task_queue']

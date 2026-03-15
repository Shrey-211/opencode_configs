"""
Task Queue System using Arq and Redis
Handles background task execution with progress tracking
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from arq import create_pool
from arq.connections import RedisSettings

from .config_loader import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskQueue:
    """Main task queue manager"""
    
    def __init__(self):
        self.redis_pool: Optional[Any] = None
        self.tasks: Dict[str, Dict[str, Any]] = {}  # task_id -> task_info
    
    async def initialize(self):
        """Initialize Redis connection pool"""
        try:
            self.redis_pool = await create_pool(
                RedisSettings(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    database=config.REDIS_DB
                )
            )
            logger.info(f"Task queue initialized with Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to initialize task queue: {e}")
            raise
    
    async def close(self):
        """Close Redis connection pool"""
        if self.redis_pool:
            await self.redis_pool.close()
            logger.info("Task queue closed")
    
    async def enqueue_task(self, task_name: str, *args, **kwargs) -> str:
        """
        Enqueue a task for background execution
        
        Returns:
            Task ID
        """
        if not self.redis_pool:
            await self.initialize()
        
        task_id = f"{task_name}_{datetime.now().timestamp()}"
        
        # Store task metadata
        self.tasks[task_id] = {
            'name': task_name,
            'args': args,
            'kwargs': kwargs,
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
            'progress': 0,
            'result': None,
            'error': None
        }
        
        # Enqueue the task
        if not self.redis_pool:
            await self.initialize()
        
        # Ensure redis_pool is not None before calling enqueue_job
        if self.redis_pool:
            await self.redis_pool.enqueue_job(task_name, *args, **kwargs, task_id=task_id)
        else:
            raise RuntimeError("Redis pool not initialized")
        
        logger.info(f"Task enqueued: {task_name} (ID: {task_id})")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task
        
        Returns:
            Task status dictionary or None if not found
        """
        return self.tasks.get(task_id)
    
    async def update_task_progress(self, task_id: str, progress: float, message: str = ""):
        """Update task progress"""
        if task_id in self.tasks:
            self.tasks[task_id]['progress'] = progress
            self.tasks[task_id]['status'] = 'running'
            if message:
                self.tasks[task_id]['message'] = message
            logger.debug(f"Task {task_id} progress: {progress}%")
    
    async def complete_task(self, task_id: str, result: Any = None):
        """Mark task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['result'] = result
            self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
            logger.info(f"Task completed: {task_id}")
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = error
            self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
            logger.error(f"Task failed: {task_id} - {error}")
    
    async def publish_progress(self, chat_id: int, message: str):
        """Publish progress update to Redis pub/sub for Telegram"""
        if self.redis_pool:
            channel = f"telegram:{chat_id}"
            await self.redis_pool.publish(channel, message)


# Global task queue instance
task_queue = TaskQueue()


# Worker functions for Arq
async def browser_automation_task(ctx, url: str, chat_id: int, task_id: str):
    """
    Background task for browser automation
    """
    redis = ctx["redis"]
    
    try:
        # Publish start message
        await redis.publish(f"telegram:{chat_id}", f"🔄 Starting browser automation for: {url}")
        
        # Update task status
        await task_queue.update_task_progress(task_id, 10, "Initializing browser...")
        
        # Simulate browser automation (replace with actual implementation)
        for i in range(100):
            await asyncio.sleep(0.1)  # Simulate work
            
            progress = i + 1
            message = f"📊 Progress: {progress}%"
            
            # Update task progress
            await task_queue.update_task_progress(task_id, progress, message)
            
            # Publish to Telegram
            if progress % 20 == 0:  # Publish every 20% to avoid spam
                await redis.publish(f"telegram:{chat_id}", message)
        
        # Complete task
        result = {"status": "completed", "url": url, "task_id": task_id}
        await task_queue.complete_task(task_id, result)
        
        # Publish completion message
        await redis.publish(f"telegram:{chat_id}", "✅ Browser automation completed!")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Browser automation failed: {str(e)}"
        await task_queue.fail_task(task_id, error_msg)
        await redis.publish(f"telegram:{chat_id}", error_msg)
        raise


async def system_check_task(ctx, chat_id: int, task_id: str):
    """
    Background task for system monitoring
    """
    redis = ctx["redis"]
    
    try:
        await redis.publish(f"telegram:{chat_id}", "🔄 Starting system check...")
        
        # Simulate system check
        import psutil
        
        await task_queue.update_task_progress(task_id, 20, "Checking CPU...")
        cpu_percent = psutil.cpu_percent(interval=1)
        
        await task_queue.update_task_progress(task_id, 50, "Checking memory...")
        memory = psutil.virtual_memory()
        
        await task_queue.update_task_progress(task_id, 80, "Checking disk...")
        disk = psutil.disk_usage('/')
        
        result = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available / (1024**3),  # GB
            "disk_percent": disk.percent,
            "disk_free": disk.free / (1024**3)  # GB
        }
        
        await task_queue.complete_task(task_id, result)
        
        # Format and send results
        message = (
            f"📊 System Check Complete:\n"
            f"CPU: {cpu_percent}%\n"
            f"Memory: {memory.percent}% ({memory.available / (1024**3):.1f} GB free)\n"
            f"Disk: {disk.percent}% ({disk.free / (1024**3):.1f} GB free)"
        )
        
        await redis.publish(f"telegram:{chat_id}", message)
        
        return result
        
    except Exception as e:
        error_msg = f"❌ System check failed: {str(e)}"
        await task_queue.fail_task(task_id, error_msg)
        await redis.publish(f"telegram:{chat_id}", error_msg)
        raise


async def long_running_task(ctx, chat_id: int, task_id: str, duration: int = 10):
    """
    Example long-running task for testing
    """
    redis = ctx["redis"]
    
    try:
        await redis.publish(f"telegram:{chat_id}", f"🔄 Starting long task ({duration}s)...")
        
        for i in range(duration * 10):  # 10 updates per second
            progress = (i / (duration * 10)) * 100
            await task_queue.update_task_progress(task_id, progress, f"Working... {progress:.1f}%")
            
            if i % 10 == 0:  # Update every second
                await redis.publish(f"telegram:{chat_id}", f"⏱️ Progress: {progress:.1f}%")
            
            await asyncio.sleep(0.1)
        
        result = {"status": "completed", "duration": duration}
        await task_queue.complete_task(task_id, result)
        await redis.publish(f"telegram:{chat_id}", "✅ Long task completed!")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Long task failed: {str(e)}"
        await task_queue.fail_task(task_id, error_msg)
        await redis.publish(f"telegram:{chat_id}", error_msg)
        raise


async def startup(ctx):
    """Arq worker startup function"""
    ctx["redis"] = await create_pool(
        RedisSettings(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            database=config.REDIS_DB
        )
    )
    logger.info("Arq worker started")


async def shutdown(ctx):
    """Arq worker shutdown function"""
    if "redis" in ctx:
        await ctx["redis"].close()
        logger.info("Arq worker shutdown")


# Worker settings for Arq
class WorkerSettings:
    functions = [
        browser_automation_task,
        system_check_task,
        long_running_task,
    ]
    cron_jobs = []  # Add scheduled tasks here if needed
    on_startup = startup
    on_shutdown = shutdown
    queue_name = "opencode_tasks"
    max_jobs = 10  # Maximum concurrent jobs


if __name__ == "__main__":
    # Test the task queue
    async def test():
        await task_queue.initialize()
        
        # Test enqueuing a task
        task_id = await task_queue.enqueue_task("long_running_task", chat_id=12345, duration=5)
        print(f"Task enqueued: {task_id}")
        
        # Wait a bit and check status
        await asyncio.sleep(2)
        status = await task_queue.get_task_status(task_id)
        print(f"Task status: {status}")
        
        await task_queue.close()
    
    asyncio.run(test())

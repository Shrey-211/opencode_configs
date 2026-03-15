"""
System Monitoring Daemon
Background service for monitoring system health and sending alerts
"""
import asyncio
import logging
import psutil
from datetime import datetime
from typing import Dict, Any

from utils import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitoringDaemon:
    """Background daemon for system monitoring"""
    
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot
        self.thresholds = {
            "cpu": config.CPU_THRESHOLD,
            "ram": config.RAM_THRESHOLD,
            "disk": config.DISK_THRESHOLD,
        }
        self.alert_sent = {
            "cpu": False,
            "ram": False,
            "disk": False
        }
        self.monitoring = False
    
    async def start(self, check_interval: int = 300):
        """
        Start the monitoring daemon
        
        Args:
            check_interval: Time between checks in seconds (default: 5 minutes)
        """
        self.monitoring = True
        logger.info(f"Starting monitoring daemon (interval: {check_interval}s)")
        
        while self.monitoring:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                
                # Check thresholds
                await self.check_thresholds(metrics)
                
                # Log metrics
                self.log_metrics(metrics)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next check
            await asyncio.sleep(check_interval)
    
    async def stop(self):
        """Stop the monitoring daemon"""
        self.monitoring = False
        logger.info("Monitoring daemon stopped")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Temperature (if available)
            cpu_temp = None
            try:
                sensors_func = getattr(psutil, 'sensors_temperatures', None)
                if sensors_func:
                    temperatures = sensors_func()
                    if 'coretemp' in temperatures:
                        cpu_temp = temperatures['coretemp'][0].current
            except:
                pass
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "net_sent_mb": net_io.bytes_sent / (1024**2),
                "net_recv_mb": net_io.bytes_recv / (1024**2),
                "cpu_temp_c": cpu_temp
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    async def check_thresholds(self, metrics: Dict[str, Any]):
        """Check if any metric exceeds threshold and send alerts"""
        alerts = []
        
        # Check CPU
        if metrics.get("cpu_percent", 0) > self.thresholds["cpu"]:
            if not self.alert_sent["cpu"]:
                alert_msg = f"⚠️ CPU usage high: {metrics['cpu_percent']}% (threshold: {self.thresholds['cpu']}%)"
                alerts.append(alert_msg)
                self.alert_sent["cpu"] = True
        else:
            self.alert_sent["cpu"] = False
        
        # Check RAM
        if metrics.get("memory_percent", 0) > self.thresholds["ram"]:
            if not self.alert_sent["ram"]:
                alert_msg = f"⚠️ RAM usage high: {metrics['memory_percent']}% (threshold: {self.thresholds['ram']}%)"
                alerts.append(alert_msg)
                self.alert_sent["ram"] = True
        else:
            self.alert_sent["ram"] = False
        
        # Check Disk
        if metrics.get("disk_percent", 0) > self.thresholds["disk"]:
            if not self.alert_sent["disk"]:
                alert_msg = f"⚠️ Disk usage high: {metrics['disk_percent']}% (threshold: {self.thresholds['disk']}%)"
                alerts.append(alert_msg)
                self.alert_sent["disk"] = True
        else:
            self.alert_sent["disk"] = False
        
        # Send alerts if any
        if alerts:
            await self.send_alerts(alerts)
    
    async def send_alerts(self, alerts: list):
        """Send alerts via Telegram"""
        if not self.telegram_bot:
            logger.warning("No Telegram bot configured for alerts")
            return
        
        message = "🚨 System Alert:\n\n" + "\n".join(alerts)
        
        # This would integrate with your Telegram bot
        # For now, just log the alerts
        logger.warning(f"System alerts: {alerts}")
        
        # TODO: Integrate with actual Telegram bot
        # await self.telegram_bot.send_message_to_all(message)
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log metrics for debugging"""
        logger.info(
            f"Metrics - CPU: {metrics.get('cpu_percent', 0):.1f}%, "
            f"RAM: {metrics.get('memory_percent', 0):.1f}%, "
            f"Disk: {metrics.get('disk_percent', 0):.1f}%"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring": self.monitoring,
            "thresholds": self.thresholds,
            "alert_sent": self.alert_sent
        }


# Global monitoring daemon instance
monitoring_daemon = MonitoringDaemon()


if __name__ == "__main__":
    # Test the monitoring daemon
    async def test():
        # Start monitoring for a short period
        daemon = MonitoringDaemon()
        
        # Collect metrics once
        metrics = await daemon.collect_metrics()
        print(f"Metrics: {metrics}")
        
        # Check thresholds
        await daemon.check_thresholds(metrics)
        
        print(f"Status: {daemon.get_status()}")
    
    asyncio.run(test())

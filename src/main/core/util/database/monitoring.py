import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from sqlalchemy.pool import Pool
from src.main.core.orm.db.base import async_db


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    total_connections: int
    available_connections: int
    utilization_percentage: float
    timestamp: float


@dataclass
class DatabaseHealthStatus:
    """Database health check status"""
    is_healthy: bool
    response_time_ms: float
    error_message: Optional[str]
    timestamp: float
    pool_stats: Optional[ConnectionPoolStats]


class DatabaseMonitor:
    """Database monitoring and health check utilities"""
    
    def __init__(self):
        self.pool: Pool = async_db.pool
        self._last_health_check: Optional[DatabaseHealthStatus] = None
        self._health_check_cache_duration = 30  # seconds
    
    def get_pool_stats(self) -> ConnectionPoolStats:
        """
        Get current connection pool statistics
        
        Returns:
            ConnectionPoolStats: Current pool statistics
        """
        try:
            pool = self.pool
            
            # Get pool statistics
            pool_size = pool.size()
            checked_in = pool.checkedin()
            checked_out = pool.checkedout()
            overflow = pool.overflow()
            invalid = pool.invalid()
            
            total_connections = checked_in + checked_out + overflow
            available_connections = pool_size - checked_out
            utilization_percentage = (checked_out / pool_size * 100) if pool_size > 0 else 0
            
            stats = ConnectionPoolStats(
                pool_size=pool_size,
                checked_in=checked_in,
                checked_out=checked_out,
                overflow=overflow,
                invalid=invalid,
                total_connections=total_connections,
                available_connections=available_connections,
                utilization_percentage=round(utilization_percentage, 2),
                timestamp=time.time()
            )
            
            logger.warning(f"Connection pool stats: {asdict(stats)}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get pool statistics: {e}")
            # Return default stats in case of error
            return ConnectionPoolStats(
                pool_size=0,
                checked_in=0,
                checked_out=0,
                overflow=0,
                invalid=0,
                total_connections=0,
                available_connections=0,
                utilization_percentage=0.0,
                timestamp=time.time()
            )
    
    async def check_database_health(self, force_check: bool = False) -> DatabaseHealthStatus:
        """
        Perform database health check
        
        Args:
            force_check: Force a new health check even if cached result is available
            
        Returns:
            DatabaseHealthStatus: Health check result
        """
        current_time = time.time()
        
        # Return cached result if available and not expired
        if (not force_check and 
            self._last_health_check and 
            current_time - self._last_health_check.timestamp < self._health_check_cache_duration):
            return self._last_health_check
        
        start_time = time.time()
        pool_stats = None
        
        try:
            # Get pool statistics
            pool_stats = self.get_pool_stats()
            
            # Test database connection with a simple query
            async with async_db.async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            
            health_status = DatabaseHealthStatus(
                is_healthy=True,
                response_time_ms=response_time_ms,
                error_message=None,
                timestamp=current_time,
                pool_stats=pool_stats
            )
            
            logger.warning(f"Database health check passed: {response_time_ms}ms")
            
        except Exception as e:
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            error_message = str(e)
            
            health_status = DatabaseHealthStatus(
                is_healthy=False,
                response_time_ms=response_time_ms,
                error_message=error_message,
                timestamp=current_time,
                pool_stats=pool_stats
            )
            
            logger.error(f"Database health check failed: {error_message} ({response_time_ms}ms)")
        
        # Cache the result
        self._last_health_check = health_status
        return health_status
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive monitoring summary
        
        Returns:
            Dict containing monitoring data
        """
        pool_stats = self.get_pool_stats()
        
        summary = {
            "pool_statistics": asdict(pool_stats),
            "health_status": asdict(self._last_health_check) if self._last_health_check else None,
            "monitoring_timestamp": time.time(),
            "alerts": self._generate_alerts(pool_stats)
        }
        
        return summary
    
    def _generate_alerts(self, pool_stats: ConnectionPoolStats) -> list:
        """
        Generate alerts based on pool statistics
        
        Args:
            pool_stats: Current pool statistics
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # High utilization alert
        if pool_stats.utilization_percentage > 80:
            alerts.append({
                "level": "warning",
                "message": f"High connection pool utilization: {pool_stats.utilization_percentage}%",
                "metric": "pool_utilization",
                "value": pool_stats.utilization_percentage
            })
        
        # Pool exhaustion alert
        if pool_stats.available_connections <= 1:
            alerts.append({
                "level": "critical",
                "message": f"Connection pool nearly exhausted: {pool_stats.available_connections} available",
                "metric": "available_connections",
                "value": pool_stats.available_connections
            })
        
        # Invalid connections alert
        if pool_stats.invalid > 0:
            alerts.append({
                "level": "warning",
                "message": f"Invalid connections detected: {pool_stats.invalid}",
                "metric": "invalid_connections",
                "value": pool_stats.invalid
            })
        
        # Overflow connections alert
        if pool_stats.overflow > pool_stats.pool_size * 0.5:
            alerts.append({
                "level": "warning",
                "message": f"High overflow connections: {pool_stats.overflow}",
                "metric": "overflow_connections",
                "value": pool_stats.overflow
            })
        
        return alerts
    
    def log_pool_status(self, level: str = "info"):
        """
        Log current pool status
        
        Args:
            level: Log level (debug, info, warning, error)
        """
        pool_stats = self.get_pool_stats()
        alerts = self._generate_alerts(pool_stats)
        
        log_message = (
            f"Database Pool Status - "
            f"Size: {pool_stats.pool_size}, "
            f"In Use: {pool_stats.checked_out}, "
            f"Available: {pool_stats.available_connections}, "
            f"Utilization: {pool_stats.utilization_percentage}%, "
            f"Overflow: {pool_stats.overflow}, "
            f"Invalid: {pool_stats.invalid}"
        )
        
        if alerts:
            log_message += f" | Alerts: {len(alerts)}"
        
        # Log based on specified level
        if level == "debug":
            logger.warning(log_message)
        elif level == "info":
            logger.info(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "error":
            logger.error(log_message)
        
        # Log alerts separately
        for alert in alerts:
            if alert["level"] == "critical":
                logger.error(f"🚨 {alert['message']}")
            elif alert["level"] == "warning":
                logger.warning(f"⚠️ {alert['message']}")


# Global monitor instance
database_monitor = DatabaseMonitor()
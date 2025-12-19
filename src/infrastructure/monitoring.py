# Performance Monitoring Service for BJJ-Trader
# Provides system metrics and API timing tracking

import time
from functools import wraps
from typing import Dict, List, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not installed. Run: pip install psutil")


class PerformanceMonitor:
    """Tracks system performance metrics and API response times."""
    
    _instance = None
    
    def __new__(cls):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.api_times: List[float] = []
        self.max_samples = 100
        self._initialized = True
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        if not PSUTIL_AVAILABLE:
            return {
                'error': 'psutil not installed',
                'cpu_percent': -1,
                'memory_percent': -1,
                'memory_mb': -1,
                'avg_api_time_ms': self._get_avg_api_time()
            }
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_mb': round(psutil.virtual_memory().used / (1024 * 1024), 2),
            'memory_available_mb': round(psutil.virtual_memory().available / (1024 * 1024), 2),
            'avg_api_time_ms': self._get_avg_api_time(),
            'api_samples': len(self.api_times)
        }
    
    def _get_avg_api_time(self) -> float:
        """Calculate average API response time."""
        if not self.api_times:
            return 0.0
        return round(sum(self.api_times) / len(self.api_times), 2)
    
    def track_api_time(self, duration_ms: float):
        """Record an API call duration."""
        self.api_times.append(duration_ms)
        if len(self.api_times) > self.max_samples:
            self.api_times.pop(0)
    
    def time_function(self, func):
        """Decorator to track function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start) * 1000
            self.track_api_time(duration_ms)
            return result
        return wrapper


# Global singleton instance
monitor = PerformanceMonitor()

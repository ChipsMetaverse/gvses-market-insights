
"""
Production Metrics Monitoring
=============================
Track key performance indicators for knowledge system.
"""

import time
import logging
from typing import Dict, List
from collections import deque
from datetime import datetime, timedelta
from threading import Lock
import asyncio

class KnowledgeMetrics:
    """Thread-safe knowledge system performance metrics."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics = {
            'retrieval_latency': deque(maxlen=window_size),
            'cache_hits': 0,
            'cache_misses': 0,
            'embedding_calls': 0,
            'total_queries': 0,
            'errors': deque(maxlen=50),
            'slow_queries': deque(maxlen=20)  # Queries > 3s
        }
        self.start_time = time.time()
        # Thread-safe lock for metrics operations
        self._lock = Lock()
        
    def record_retrieval(self, duration: float, cache_hit: bool = False):
        """Record a knowledge retrieval event (thread-safe)."""
        with self._lock:
            self.metrics['retrieval_latency'].append(duration)
            self.metrics['total_queries'] += 1
            
            if cache_hit:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['cache_misses'] += 1
                
            if duration > 3.0:
                self.metrics['slow_queries'].append({
                    'duration': duration,
                    'timestamp': datetime.now(),
                    'cache_hit': cache_hit
                })
            
    def record_embedding_call(self):
        """Record an embedding API call (thread-safe)."""
        with self._lock:
            self.metrics['embedding_calls'] += 1
        
    def record_error(self, error: str):
        """Record an error event (thread-safe)."""
        with self._lock:
            self.metrics['errors'].append({
                'error': error,
                'timestamp': datetime.now()
            })
        
    def get_stats(self) -> Dict:
        """Get current metrics statistics (thread-safe)."""
        with self._lock:
            latencies = list(self.metrics['retrieval_latency'])
            cache_total = self.metrics['cache_hits'] + self.metrics['cache_misses']
            
            stats = {
                'uptime_hours': (time.time() - self.start_time) / 3600,
                'total_queries': self.metrics['total_queries'],
                'avg_latency_ms': sum(latencies) / len(latencies) * 1000 if latencies else 0,
                'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)] * 1000 if latencies else 0,
                'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)] * 1000 if latencies else 0,
                'cache_hit_rate': self.metrics['cache_hits'] / cache_total if cache_total > 0 else 0,
                'embedding_calls': self.metrics['embedding_calls'],
                'recent_errors': len(self.metrics['errors']),
                'slow_queries_count': len(self.metrics['slow_queries'])
            }
        
        # Check SLAs
        stats['meets_latency_sla'] = stats['avg_latency_ms'] < 200
        stats['meets_cache_sla'] = stats['cache_hit_rate'] > 0.5
        
        return stats
        
    def log_metrics(self):
        """Log current metrics to console/monitoring system."""
        stats = self.get_stats()
        
        logger = logging.getLogger(__name__)
        logger.info("=== Knowledge System Metrics ===")
        logger.info(f"Queries: {stats['total_queries']}")
        logger.info(f"Avg Latency: {stats['avg_latency_ms']:.0f}ms (SLA: <200ms) {'✅' if stats['meets_latency_sla'] else '❌'}")
        logger.info(f"P95 Latency: {stats['p95_latency_ms']:.0f}ms")
        logger.info(f"Cache Hit Rate: {stats['cache_hit_rate']:.1%} {'✅' if stats['meets_cache_sla'] else '❌'}")
        logger.info(f"Slow Queries: {stats['slow_queries_count']}")
        logger.info(f"Recent Errors: {stats['recent_errors']}")

# Integration example:
# In agent_orchestrator.py, add:
# self.metrics = KnowledgeMetrics()
# 
# When retrieving knowledge:
# start = time.time()
# knowledge = await self._get_cached_knowledge(query)
# self.metrics.record_retrieval(time.time() - start, cache_hit=was_cached)

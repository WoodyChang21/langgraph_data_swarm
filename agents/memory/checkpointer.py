
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import structlog
import asyncio

from dotenv import load_dotenv
import os
from pathlib import Path
import uuid

from agents.llm_model import LLM

# Initialize logger
logger = structlog.get_logger()
load_dotenv()

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6381/0")

# Redis connection parameters for stability
# Keep it simple - only essential timeout settings
REDIS_CONN_KWARGS = {
    "socket_timeout": 300,  # 5 minutes for long graph operations
    "socket_connect_timeout": 10,  # Connection establishment timeout
    "socket_keepalive": True,  # Prevent connection drops
    "retry_on_timeout": True,  # Auto-retry on timeout
    "health_check_interval": 30,  # Periodic connection health check
}


# Define Pre Model Hook to manage history length
model = LLM

# This is for Redis Chat Storage Settings
TTL_MINUTES = 60  # e.g., expire after 60 minutes of inactivity
ttl_config = {
    "default_ttl": TTL_MINUTES,  # TTL is in minutes
    "refresh_on_read": True,  # touching a thread resets its TTL
}

# ========== SINGLETON CHECKPOINTER ==============
# Shared checkpointer for all requests - thread-safe singleton
_checkpointer = None
_checkpointer_lock = asyncio.Lock()

async def get_shared_checkpointer():
    """
    Get or create the shared Redis checkpointer.
    This is a thread-safe singleton that reuses the same connection.
    Different users are isolated via thread_id in the config.
    """
    global _checkpointer
    
    if _checkpointer is None:
        async with _checkpointer_lock:
            # Double-check pattern to avoid race conditions
            if _checkpointer is None:
                logger.info("Initializing shared Redis checkpointer", redis_url=REDIS_URL)
                _checkpointer = await AsyncRedisSaver.from_conn_string(
                    REDIS_URL,
                    ttl=ttl_config,
                    connection_args=REDIS_CONN_KWARGS
                ).__aenter__()
                logger.info("Shared Redis checkpointer initialized successfully")
    
    return _checkpointer

if __name__ == "__main__":
    if asyncio.run(get_shared_checkpointer()):
        print("TRUE")
"""
Memory Management for Multi-Agent Swarm

Simple, production-ready message trimming to prevent tool call errors.
"""

from langchain_core.messages import trim_messages
from typing import Any
import structlog
import os
from dotenv import load_dotenv

load_dotenv()

logger = structlog.get_logger()

# Configuration
MAX_MESSAGES = 50  
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ==================== MAIN FUNCTION (Use This in pre_model_hook) ====================

def trim_for_agent(state: dict) -> dict:
    """
    Trim message history before sending to LLM.
    
    USE THIS in create_react_agent's pre_model_hook parameter!
    
    Features:
    - Keeps last 20 messages (configurable)
    - Always preserves system messages
    - Starts on "human" to prevent incomplete tool calls
    - Prevents "tool_calls without ToolMessage" errors
    
    Args:
        state: Agent state dict containing "messages" key
        
    Returns:
        State dict with trimmed messages
    """
    
    if "messages" not in state:
        logger.warning("No messages in state, returning empty")
        return {"messages": []}
    
    messages = state["messages"]
    
    # Skip trimming if under limit
    if len(messages) <= MAX_MESSAGES:
        logger.debug("Under message limit, no trimming needed", count=len(messages), limit=MAX_MESSAGES)
        return {"messages": messages}
    
    try:
        # Use LangChain's trim_messages with safety features
        trimmed = trim_messages(
            messages,
            max_tokens=MAX_MESSAGES,  # Rough estimate (adjust as needed)
            strategy="last",  # Keep most recent
            token_counter=lambda msgs: len(msgs),  # Simple counter
            include_system=True,  # Always keep system prompts
            allow_partial=False,  # Don't split messages
            start_on="human",  # ← KEY: Prevents incomplete tool calls!
        )
        
        logger.info(
            "Trimmed messages",
            original=len(messages),
            trimmed=len(trimmed),
            removed=len(messages) - len(trimmed)
        )
        
        # Return only the messages key to avoid "unknown channel" warnings
        return {"messages": trimmed}
    
    except Exception as e:
        logger.error("Trimming failed, keeping all messages", error=str(e))
        return {"messages": messages}  # Return original messages as dict


# ==================== Cleanup Utilities ====================

async def clear_thread(user_id: str):
    """Clear corrupted thread from Redis (use when getting tool call errors)"""
    import redis.asyncio as redis
    
    try:
        r = await redis.from_url(REDIS_URL)
        keys = [key async for key in r.scan_iter(match=f"*{user_id}*")]
        
        if keys:
            await r.delete(*keys)
            logger.info(f"Cleared {len(keys)} keys", user_id=user_id)
        
        await r.close()
        return True
    except Exception as e:
        logger.error("Error clearing thread", user_id=user_id, error=str(e))
        return False


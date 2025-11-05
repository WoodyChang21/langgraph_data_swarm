"""
Chat completion router - OpenAI-compatible endpoints
"""

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import structlog

from agents.swarm.swarm import airport_swarm

logger = structlog.get_logger()

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "airport-swarm"
    messages: List[Message]
    stream: Optional[bool] = False
    user: Optional[str] = None


@router.post("/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest,
    x_openwebui_user_id: Optional[str] = Header(None, alias="X-OpenWebUI-Chat-Id")
):
    """
    OpenAI-compatible chat completions endpoint.
    
    Supports both streaming and non-streaming responses.
    """
    try:
        # Extract user_id from request or use default
        user_id = x_openwebui_user_id or req.user or "openwebui_user"
        
        # Get the last user message
        user_message = req.messages[-1].content if req.messages else ""
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No message content provided")
        
        logger.info("Received chat request", user_id=user_id, message_preview=user_message[:100])
        
        # Route based on streaming preference
        if req.stream:
            logger.info("USING STREAM RESPONSE")
            return StreamingResponse(
                stream_response(user_id, user_message, req.model),
                media_type="text/event-stream"
            )
        else:
            logger.info("USING NON-STREAM RESPONSE")
            return await non_streaming_response(user_id, user_message, req.model)
    
    except Exception as e:
        logger.error("Error processing request", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def non_streaming_response(user_id: str, message: str, model: str) -> Dict[str, Any]:
    """
    Non-streaming response (all at once).
    """
    try:
        # Invoke the swarm
        answer = await airport_swarm.invoke(user_id=user_id, message=message)
        
        # Ensure answer is a clean string (defensive programming)
        if not isinstance(answer, str):
            logger.warning("Answer is not a string, converting", type=type(answer))
            answer = str(answer)
        
        # Log for debugging
        
        return {
            "id": f"chatcmpl-{user_id}",
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": model or "airport-swarm",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer  # Guaranteed to be a string now
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # Not tracking for now
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        logger.error("Error in non-streaming response", error=str(e))
        raise


async def stream_response(user_id: str, message: str, model: str):
    """
    Stream with subgraphs=True to show intermediate progress
    """
    try:
        seen_message_ids = set()
        
        async for chunk in airport_swarm.stream(user_id=user_id, message=message):
            
            # Handle subgraphs mode (tuple format)
            if isinstance(chunk, tuple):
                namespace, data = chunk
                
                # Skip parent-level summary chunks (empty namespace)
                if not namespace or namespace == ():
                    logger.info("Skipping parent-level summary chunk")
                    continue
                
                # Process subgraph chunks (shows intermediate steps)
                for node_name, node_data in data.items():
                    if isinstance(node_data, dict) and 'messages' in node_data:
                        for msg in node_data['messages']:
                            msg_id = getattr(msg, 'id', None)
                            
                            # Skip duplicates
                            if msg_id and msg_id in seen_message_ids:
                                continue
                            if msg_id:
                                seen_message_ids.add(msg_id)
                            
                            # Skip user messages
                            if type(msg).__name__ == "HumanMessage":
                                continue
                            
                            # Stream tool calls in OpenAI format for rich UI display
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                logger.info("Streaming tool calls", 
                                        node=node_name,
                                        num_calls=len(msg.tool_calls))

                                openai_tool_calls = []
                                for idx, tool_call in enumerate(msg.tool_calls):
                                    openai_tool_calls.append({
                                        "index": idx,
                                        "id": tool_call.get('id', f"call_{msg_id}_{idx}"),
                                        "type": "function",
                                        "function": {
                                            "name": tool_call.get('name', 'unknown'),
                                            "arguments": json.dumps(tool_call.get('args', {}))
                                        }
                                    })

                                event = {
                                    "id": f"chatcmpl-{user_id}",
                                    "object": "chat.completion.chunk",
                                    "created": int(asyncio.get_event_loop().time()),
                                    "model": model or "airport-swarm",
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "tool_calls": openai_tool_calls   # ✅ no role
                                        },
                                        "finish_reason": "tool_calls"
                                    }]
                                }

                                yield f"data: {json.dumps(event)}\n\n"
                                continue

                            
                            # Stream tool results in OpenAI format
                            if type(msg).__name__ == "ToolMessage":
                                tool_content = getattr(msg, 'content', '')
                                tool_call_id = getattr(msg, 'tool_call_id', None)
                                
                                if tool_content:
                                    logger.info("Streaming tool result", 
                                               tool_call_id=tool_call_id,
                                               preview=str(tool_content)[:100])
                                    
                                    # Send tool result in OpenAI format
                                    event = {
                                        "id": f"chatcmpl-{user_id}",
                                        "object": "chat.completion.chunk",
                                        "created": int(asyncio.get_event_loop().time()),
                                        "model": model or "airport-swarm",
                                        "choices": [{
                                            "index": 0,
                                            "delta": {
                                                "role": "tool",
                                                "tool_call_id": tool_call_id,
                                                "content": str(tool_content)
                                            },
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(event)}\n\n"
                                continue
                            
                            # Stream final AI responses
                            content = getattr(msg, 'content', '')
                            if content:
                                event = {
                                    "id": f"chatcmpl-{user_id}",
                                    "object": "chat.completion.chunk",
                                    "created": int(asyncio.get_event_loop().time()),
                                    "model": model or "airport-swarm",
                                    "choices": [{
                                        "index": 0,
                                        "delta": {"content": content},
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(event)}\n\n"
        
        # Final chunk
        final_event = {
            "id": f"chatcmpl-{user_id}",
            "object": "chat.completion.chunk",
            "created": int(asyncio.get_event_loop().time()),
            "model": model or "airport-swarm",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(final_event)}\n\n"
        yield "data: [DONE]\n\n"
    
    except Exception as e:
        logger.error("Error in streaming response", error=str(e))
        error_event = {
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": 500
            }
        }
        yield f"data: {json.dumps(error_event)}\n\n"


@router.get("/models")
async def list_models():
    """
    List available models (OpenAI-compatible).
    OpenWebUI calls this to discover models.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "airport-swarm",
                "object": "model",
                "created": 1699000000,
                "owned_by": "airport-ai",
                "permission": [],
                "root": "airport-swarm",
                "parent": None
            }
        ]
    }


# Utility function for clearing chat history
async def clear_user_history(user_id: str):
    """Clear Redis chat history for a user"""
    await airport_swarm.clear_thread(user_id)
    return {"status": "cleared", "user_id": user_id}


# Test function for streaming
async def test_streaming(messages: str):
    """Test the streaming response locally"""
    print("=" * 80)
    print("Testing Stream Response")
    print("=" * 80)
    
    user_id = "test_user"
    message = messages
    model = "airport-swarm"
    
    print(f"\nUser: {message}\n")
    print("Streaming chunks:\n")
    
    chunk_count = 0
    async for sse_chunk in stream_response(user_id, message, model):
        chunk_count += 1
        print(f"Chunk #{chunk_count}:")
        print(sse_chunk)
        print("-" * 40)
    
    print(f"\nTotal SSE chunks: {chunk_count}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    # Test the streaming method
    messages = "Give me the number of flights from Taiwan to Japan in every month in 2025 and visualize it in a bar chart"
    messages = "Hi"
    asyncio.run(test_streaming(messages))
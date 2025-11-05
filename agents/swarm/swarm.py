"""
LangGraph Swarm Multi-Agent System for Airport Data Analysis

This module implements a swarm of specialized agents:
1. SQL Agent: Handles database queries and exports data to CSV/S3
2. Plot Agent: Creates visualizations from the data

The agents can hand off tasks to each other and share data through:
- CSV files (local storage)
- S3 URLs (cloud storage)
- Redis checkpointer (conversation memory)
"""

import asyncio
import structlog
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

from agents.llm_model import LLM
from agents.sql_search_agent.sql_agent import SQLiteAgent
from agents.plot_agent.plot_agent import PlotAgent
from agents.memory.checkpointer import get_shared_checkpointer
from agents.memory.memory_manager import trim_for_agent
from agents.swarm.sql_agent_with_handoff import create_sql_agent_with_handoff
from agents.swarm.plot_agent_with_handoff import create_plot_agent_with_handoff
from agents.memory.memory_manager import clear_thread

load_dotenv()

logger = structlog.get_logger()


class AirportAgentSwarm:
    """
    Multi-agent swarm system for airport data analysis.
    
    Workflow:
    1. User asks a question → SQL Agent queries database
    2. SQL Agent exports data to CSV and S3
    3. SQL Agent can hand off to Plot Agent with CSV path/S3 URL
    4. Plot Agent reads the data and creates visualizations
    """
    
    def __init__(self):
        """Initialize the swarm class (synchronous, no async calls here)"""
        self.llm = LLM
        self.app = None
        self._initialized = False  # Track initialization state
    
    async def clear_thread(self, user_id: str):
        """
        Clear corrupted thread history from Redis.
        
        Use when encountering: "tool_calls without ToolMessage" error
        
        Args:
            user_id: User/thread ID to clear
        """
        return await clear_thread(user_id)
    
    async def initialize(self):
        """
        Initialize the swarm with both agents (lazy initialization pattern).
        Called automatically on first invoke() - only runs once.
        """
        # Check if already initialized (singleton pattern)
        if self._initialized:
            logger.info("Swarm already initialized, reusing")
            return self.app
        
        logger.info("Initializing Airport Agent Swarm (first time, global instance)")
        
        # Create agents with handoff capabilities (no user_id - runtime extraction!)
        sql_agent = await create_sql_agent_with_handoff()
        plot_agent = await create_plot_agent_with_handoff()
        
        # Get shared checkpointer (singleton Redis connection)
        checkpointer = await get_shared_checkpointer()
        
        # Create swarm workflow
        workflow = create_swarm(
            agents=[sql_agent, plot_agent],
            default_active_agent="SQLAgent"  # Start with SQL agent
        )
        
        # Compile the workflow (ONCE for all users)
        self.app = workflow.compile(checkpointer=checkpointer)
        self._initialized = True
        
        logger.info("Airport Agent Swarm initialized successfully (global, optimized)")
        return self.app
    
    async def invoke(self, user_id: str, message: str):
        """
        Invoke the swarm with a user message.
        
        Args:
            user_id: Unique identifier for the user (used for thread_id)
            message: User's question or request
            
        Returns:
            The final response from the active agent
        """
        # Lazy initialization: compile swarm on first use
        if not self._initialized:
            await self.initialize()
        
        # User isolation via thread_id (not separate swarms!)
        config = {"configurable": {"thread_id": user_id}}
        
        # Trim conversation ONCE before invoking (trim_for_agent handles conditions & logging)
        try:
            current_state = await self.app.aget_state(config)
            logger.info("Current Message Length", length=len(current_state.values.get("messages", [])))
            if current_state and current_state.values:
                # Get current messages
                current_messages = current_state.values.get("messages", [])
                # trim_for_agent handles: condition check, trimming, and logging
                trimmed_result = trim_for_agent({"messages": current_messages})
                # Update state if messages were modified
                if "messages" in trimmed_result:
                    await self.app.aupdate_state(config, trimmed_result)
        
        except Exception as e:
            logger.warning("Could not trim before invoke", user_id=user_id, error=str(e))
            # Continue anyway - trimming failure shouldn't block requests
        
        logger.info("Invoking swarm", user_id=user_id, message=message)
        
        result = await self.app.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )
        
        final_message = result["messages"][-1].content
        
        return final_message
    
    async def stream(self, user_id: str, message: str):
        """
        Stream responses from the swarm (for real-time updates).
        
        Args:
            user_id: Unique identifier for the user
            message: User's question or request
            
        Yields:
            Intermediate and final messages from agents
        """
        # Lazy initialization: compile swarm on first use
        if not self._initialized:
            await self.initialize()
        
        # User isolation via thread_id (not separate swarms!)
        config = {"configurable": {"thread_id": user_id}}
        
        # ✅ Trim conversation ONCE before invoking (trim_for_agent handles conditions & logging)
        try:
            current_state = await self.app.aget_state(config)
            logger.info("Current Message Length", length=len(current_state.values.get("messages", [])))
            if current_state and current_state.values:
                # Get current messages
                current_messages = current_state.values.get("messages", [])
                # trim_for_agent handles: condition check, trimming, and logging
                trimmed_result = trim_for_agent({"messages": current_messages})
                # Update state if messages were modified
                if "messages" in trimmed_result:
                    await self.app.aupdate_state(config, trimmed_result)
        
        except Exception as e:
            logger.warning("Could not trim before invoke", user_id=user_id, error=str(e))
            # Continue anyway - trimming failure shouldn't block requests
        
        logger.info("Streaming swarm", user_id=user_id, message=message)
        
        # For OpenWebUI: Just use invoke and return complete response
        # Streaming intermediate steps would show tool calls, which confuses users
        async for chunk in self.app.astream(
            config=config, 
            stream_mode="updates", 
            subgraphs=True,
            input={"messages": [{"role": "user", "content": message}]}):
            yield chunk


# Global swarm instance
airport_swarm = AirportAgentSwarm()


async def test_invoke():
    """
    Example usage of the Airport Agent Swarm
    """
    user_id = "interactive_user"
    
    print("=" * 80)
    print("Airport Agent Swarm - Interactive Demo")
    print("=" * 80)
    print("\nAvailable agents:")
    print("  1. SQLAgent - Queries airport database and exports data")
    print("  2. PlotAgent - Creates visualizations from data")
    print("\nDatabase date range: August 2024 - July 2025")
    print("\nExample queries:")
    print("  - '2025年1月從日本出發的航班有哪些？請匯出CSV並繪製圖表'")
    print("  - 'Show me arrival flights from Korea in January 2025 and create a bar chart by destination'")
    print("  - 'Query departure data between 2024-12-01 and 2024-12-31 and visualize the top destinations'")
    print("  - 'Get flights from Taiwan in 2025-01 and create a pie chart by airline'")
    print("\nType 'exit' to quit\n")
    
    while True:
        print("-" * 80)
        user_input = input("Your question: ").strip()
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Invoke the swarm
            response = await airport_swarm.invoke(user_id, user_input)
            print(f"\n🤖 Response:\n{response}\n")
            
        except Exception as e:
            logger.error("Error in swarm execution", error=str(e))
            print(f"\n❌ Error: {str(e)}\n")

async def test_stream():
    user_id = "interactive_user"
    message = "Hi, who are you?"
    async for chunk in airport_swarm.stream(user_id, message):
        yield chunk

if __name__ == "__main__":
    asyncio.run(test_invoke())
    # asyncio.run(test_stream())
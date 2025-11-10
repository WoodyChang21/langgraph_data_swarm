"""
LangGraph Swarm Multi-Agent System for Airport Data Analysis

This module implements a swarm of specialized agents:
1. SQL Agent: Handles database queries and exports data to CSV/S3
2. Analysis Agent: Performs statistical analysis and data transformations
3. Plot Agent: Creates visualizations from the data

The agents can hand off tasks to each other and share data through:
- CSV files (local storage)
- S3 URLs (cloud storage)
"""

import asyncio
import structlog
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

from agents.llm_model import LLM
from agents.swarm.sql_agent_with_handoff import create_sql_agent_with_handoff
from agents.swarm.analysis_agent_with_handoff import create_analysis_agent_with_handoff
from agents.swarm.plot_agent_with_handoff import create_plot_agent_with_handoff

load_dotenv()

logger = structlog.get_logger()


class AirportAgentSwarm:
    """
    Multi-agent swarm system for airport data analysis.
    
    Workflow:
    1. User asks a question → SQL Agent queries database
    2. SQL Agent exports data to CSV and S3
    3. SQL Agent can hand off to:
       - Analysis Agent: For statistical analysis, aggregations, transformations
       - Plot Agent: For visualizations and charts
    4. Analysis Agent can hand off to:
       - Plot Agent: For visualizing analyzed results
       - SQL Agent: For requesting different/additional data
    5. Plot Agent can hand off to:
       - Analysis Agent: For deeper analysis of plotted data
       - SQL Agent: For requesting different/additional data
    """
    
    def __init__(self):
        """Initialize the swarm class (synchronous, no async calls here)"""
        self.llm = LLM
        self.app = None
        self._initialized = False  # Track initialization state
    
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
        analysis_agent = await create_analysis_agent_with_handoff()
        plot_agent = await create_plot_agent_with_handoff()
        
        
        # Create swarm workflow
        workflow = create_swarm(
            agents=[sql_agent, analysis_agent, plot_agent],
            default_active_agent="SQLAgent"  # Start with SQL agent
        )
        
        # Compile the workflow (ONCE for all users)
        self.app = workflow.compile()
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
    print("  2. AnalysisAgent - Performs statistical analysis and data transformations")
    print("  3. PlotAgent - Creates visualizations from data")
    print("\nDatabase date range: August 2024 - July 2025")
    print("\nExample queries:")
    print("\nSQL + Analysis:")
    print("  - 'Query January 2025 Japan flights and analyze average passengers by airline'")
    print("  - 'Get Korea departure data and calculate correlation between time and passenger count'")
    print("\nSQL + Plot:")
    print("  - '2025年1月從日本出發的航班有哪些？請匯出CSV並繪製圖表'")
    print("  - 'Show me arrival flights from Korea in January 2025 and create a bar chart'")
    print("\nSQL + Analysis + Plot:")
    print("  - 'Query December 2024 flights, analyze top destinations, then visualize results'")
    print("  - 'Get Taiwan flights in 2025-01, calculate statistics, and create a pie chart by airline'")
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
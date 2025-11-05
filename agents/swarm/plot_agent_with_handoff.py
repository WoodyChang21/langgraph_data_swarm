from langgraph_swarm import create_handoff_tool
from langgraph.prebuilt import create_react_agent

from agents.plot_agent.plot_agent import PlotAgent
from agents.llm_model import LLM

plot_agent_instance = PlotAgent()

async def create_plot_agent_with_handoff():
    """Create Plot agent with handoff tool back to SQL Agent"""
    # Get Plot agent's tools
    plot_tools = plot_agent_instance._get_tools()
    
    # Add handoff tool back to SQL Agent
    handoff_to_sql = create_handoff_tool(
        agent_name="SQLAgent",
        description=(
            "Transfer to SQL Agent when the user needs new data from the database. "
            "Use this when you need different data or when user asks database-related questions."
        )
    )
    
    plot_system_prompt = plot_agent_instance._get_system_prompt()
    enhanced_plot_prompt = f"""{plot_system_prompt}

        WORKFLOW:
        1. SQL Agent hands off with CSV URL → Read data → Create plot → Respond
        2. After creating plot: **STOP and respond to user** - do NOT hand back automatically
        3. Only use 'transfer_to_sqlagent' if user explicitly asks for NEW data

        CRITICAL: Do NOT call transfer_to_sqlagent multiple times!
        - After calling handoff tool once → STOP
        - Do not continue reasoning after handoff

        Example: User asks for different data
        → Call transfer_to_sqlagent ONCE → DONE! Do not call again."""
    
    plot_agent = create_react_agent(
        LLM,
        plot_tools + [handoff_to_sql],
        prompt=enhanced_plot_prompt,
        name="PlotAgent"
    )
    
    return plot_agent

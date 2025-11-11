from langgraph_swarm import create_handoff_tool
from langgraph.prebuilt import create_react_agent
from agents.swarm.handoff_tool import create_task_description_handoff_tool

from agents.plot_agent.plot_agent import PlotAgent
from agents.llm_model import LLM

plot_agent_instance = PlotAgent()

async def create_plot_agent_with_handoff():
    """Create Plot agent with handoff tool back to SQL Agent"""
    # Get Plot agent's tools
    plot_tools = plot_agent_instance._get_tools()
    
    # Add handoff tool back to SQL Agent
    # handoff_to_sql = create_handoff_tool(
    #     agent_name="SQLAgent",
    #     description=(
    #         "Transfer to SQL Agent when the user needs new data from the database. "
    #         "Use this when you need different data or when user asks database-related questions."
    #     )
    # )

    # handoff_to_analysis = create_handoff_tool(
    #     agent_name="AnalysisAgent",
    #     description=(
    #         "Transfer to Analysis Agent when the user wants to perform statistical analysis or data transformations. "
    #     )
    # )
    handoff_to_sql = create_task_description_handoff_tool(
        agent_name="SQLAgent",
        description=(
            "Transfer to SQL Agent when the user wants to query the database for new or different data. "
            "Use this when current dataset is insufficient or user requests different data. "
        )
    )
    handoff_to_analysis = create_task_description_handoff_tool(
        agent_name="AnalysisAgent",
        description=(
            "Transfer to Analysis Agent when the user wants to perform statistical analysis or data transformations. "
            "Make sure the data S3 URL is mentioned in the task description. "
        )
    )
    
    plot_system_prompt = plot_agent_instance._get_system_prompt()
    enhanced_plot_prompt = f"""{plot_system_prompt}

    HANDOFF SUMMARY:
    - To Analysis Agent → For analysis or insights on current data
    - To SQL Agent → For new data or database queries
    - Only one handoff tool should be used at a time.
    - After handoff, STOP reasoning immediately.

    NEVER DO THIS (causes system error):
    - transfer_to_[agentname]("task description 1")
    - transfer_to_[agentname]("task description 2")  # SECOND CALL = ERROR!

    ALWAYS DO THIS (correct):
    - transfer_to_[agentname]("task description 1 AND task description 2")
    """
    
    plot_agent = create_react_agent(
        LLM,
        plot_tools + [handoff_to_sql, handoff_to_analysis],
        # plot_tools + [handoff_to_sql],
        prompt=enhanced_plot_prompt,
        name="PlotAgent"
    )
    
    return plot_agent

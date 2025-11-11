from langgraph_swarm import create_handoff_tool
from langgraph.prebuilt import create_react_agent

from agents.analysis_agent.analysis_agent import AnalysisAgent
from agents.llm_model import LLM
from agents.swarm.handoff_tool import create_task_description_handoff_tool

analysis_agent_instance = AnalysisAgent()

async def create_analysis_agent_with_handoff():
    """Create Analysis agent with handoff tools to SQL Agent and Plot Agent"""
    # Get Analysis agent's tools
    analysis_tools = analysis_agent_instance._get_tools()
    
    # Add handoff tool to SQL Agent
    # handoff_to_sql = create_handoff_tool(
    #     agent_name="SQLAgent",
    #     description=(
    #         "Transfer to SQL Agent when the user wants to query the database for new or different data. "
    #         "Use this when current dataset is insufficient or user requests different data. "
    #     )
    # )

    # # Add handoff tool to Plot Agent
    # handoff_to_plot = create_handoff_tool(
    #     agent_name="PlotAgent",
    #     description=(
    #         "Transfer to Plot Agent when user wants to visualize the analyzed data. "
    #     )
    # )
    handoff_to_sql = create_task_description_handoff_tool(
        agent_name="SQLAgent",
        description=(
            "Transfer to SQL Agent when the user wants to query the database for new or different data. "
            "Use this when current dataset is insufficient or user requests different data. "
        )
    )
    handoff_to_plot = create_task_description_handoff_tool(
        agent_name="PlotAgent",
        description=(
            "Transfer to Plot Agent when user wants to visualize the analyzed data. "
            "Make sure the data S3 URL is mentioned in the task description. "
        )
    )
    
    analysis_system_prompt = analysis_agent_instance._get_system_prompt()
    enhanced_analysis_prompt = f"""{analysis_system_prompt}

    HANDOFF SUMMARY:
    - To SQL Agent → For new or different data from the database
    - To Plot Agent → For charts, graphs, or visualizations
    - Only one handoff tool should be used at a time.
    - After handoff, STOP reasoning immediately.

    NEVER DO THIS (causes system error):
    - transfer_to_[agentname]("task description 1")
    - transfer_to_[agentname]("task description 2")  # SECOND CALL = ERROR!

    ALWAYS DO THIS (correct):
    - transfer_to_[agentname]("task description 1 AND task description 2")
    """
    
    analysis_agent = create_react_agent(
        LLM,
        analysis_tools + [handoff_to_sql, handoff_to_plot],
        prompt=enhanced_analysis_prompt,
        name="AnalysisAgent"
    )
    
    return analysis_agent
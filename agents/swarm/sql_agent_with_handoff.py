from langgraph_swarm import create_handoff_tool
from langgraph.prebuilt import create_react_agent
from agents.sql_search_agent.sql_agent import SQLiteAgent
from agents.llm_model import LLM
from agents.swarm.handoff_tool import create_task_description_handoff_tool

sql_agent_instance = SQLiteAgent()

async def create_sql_agent_with_handoff():
    """Create SQL agent with handoff tool to Plot Agent"""
    # Get SQL agent's tools
    sql_tools = sql_agent_instance._get_tools()
    
    # Add handoff tool to Plot Agent
    # handoff_to_plot = create_handoff_tool(
    #     agent_name="PlotAgent",
    #     description=(
    #         "Transfer to Plot Agent when the user wants to visualize data."
    #         "Do not handoff to plot agent if the agent hasn't yet exported the data to CSV file. "
    #         "Only use this after generating CSV data. "
    #         "Always make sure the data S3 URL is mentioned in your previous message before handing off. "
    #     )
    # )

    # handoff_to_analysis = create_handoff_tool(
    #     agent_name="AnalysisAgent",
    #     description=(
    #         "Transfer to Analysis Agent when the user wants to perform statistical analysis or data transformations. "
    #         "Use this after exporting CSV data. "
    #         "Make sure `sql_query_with_csv_export` was called and returned the data S3 URL in your previous message before handing off. "
    #     )
    # )

    handoff_to_plot = create_task_description_handoff_tool(
        agent_name="PlotAgent",
        description=(
            "Transfer to Plot Agent when the user wants to visualize data."
            "Do not handoff to plot agent if the agent hasn't yet exported the data to CSV file. "
            "Only use this after generating CSV data. Make sure the data S3 URL is mentioned in the task description. "
        )
    )
    handoff_to_analysis = create_task_description_handoff_tool(
        agent_name="AnalysisAgent",
        description=(
            "Transfer to Analysis Agent when the user wants to perform statistical analysis or data transformations. "
            "Use this after exporting CSV data. Make sure the data S3 URL is mentioned in the task description. "
            "Make sure `sql_query_with_csv_export` was called and did return the S3 URL."
        )
    )

    sql_system_prompt = sql_agent_instance._get_system_prompt()
    enhanced_sql_prompt = f"""{sql_system_prompt}

    HANDOFF SUMMARY:
    - To Analysis Agent → For statistical analysis, aggregations, or calculations
    - To Plot Agent → For charts, graphs, or visualizations
    - Only one handoff tool should be used at a time.
    - After handoff, STOP reasoning immediately.

    NEVER DO THIS (causes system error):
    - transfer_to_[agentname]("task description 1")
    - transfer_to_[agentname]("task description 2")  # SECOND CALL = ERROR!

    ALWAYS DO THIS (correct):
    - transfer_to_[agentname]("task description 1 AND task description 2")
    """
    
    sql_agent = create_react_agent(
        LLM,
        sql_tools + [handoff_to_plot, handoff_to_analysis],
        prompt=enhanced_sql_prompt,
        name="SQLAgent"
    )
    
    return sql_agent
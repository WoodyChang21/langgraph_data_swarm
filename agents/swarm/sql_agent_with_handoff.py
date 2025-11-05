from langgraph_swarm import create_handoff_tool
from langgraph.prebuilt import create_react_agent
from agents.sql_search_agent.sql_agent import SQLiteAgent
from agents.llm_model import LLM


sql_agent_instance = SQLiteAgent()

async def create_sql_agent_with_handoff():
    """Create SQL agent with handoff tool to Plot Agent"""
    # Get SQL agent's tools
    sql_tools = sql_agent_instance._get_tools()
    
    # Add handoff tool to Plot Agent
    handoff_to_plot = create_handoff_tool(
        agent_name="PlotAgent",
        description=(
            "Transfer to Plot Agent when the user wants to visualize data."
            "Use this after generating CSV data. "
            "Always provide the CSV file path or S3 URL in your message when handing off. "
            "Example: 'I've created a CSV with flight data at [S3_URL]. "
            "Please create a bar chart showing flights by destination.'"
        )
    )
    
    sql_system_prompt = sql_agent_instance._get_system_prompt()
    enhanced_sql_prompt = f"""{sql_system_prompt}

        HANDOFF TO PLOT AGENT:
        When user wants visualization after you've generated data:
        1. Use 'sql_query_with_csv_export' to export data
        2. Call 'transfer_to_plotagent' ONCE with the S3 URL
        3. **STOP** - Do not call transfer_to_plotagent again
        4. Do not continue reasoning after handoff

        Example: "I've exported data to [S3_URL]. Please create a bar chart."
        → Call transfer_to_plotagent → DONE!"""
    
    sql_agent = create_react_agent(
        LLM,
        sql_tools + [handoff_to_plot],
        prompt=enhanced_sql_prompt,
        name="SQLAgent"
    )
    
    return sql_agent
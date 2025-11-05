import os
import json
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Annotated

from langchain_core.tools import Tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langsmith import Client
from langchain_core.messages import HumanMessage

from agents.sql_search_agent.s3_csv_utils import s3_csv_uploader
from agents.llm_model import LLM
from agents.memory.checkpointer import get_shared_checkpointer

load_dotenv()

SQL_DATABASE_PATH = os.getenv("SQL_DATABASE_PATH")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# PATHS
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_PATH, "csv") # Used in _get_csv_export_tool
AIRPORT_MAPPING_PATH = os.path.join(BASE_PATH, "search_prompt", "airport_mapping.json") # Used in _get_country_airport_tool
SEARCH_PROMPT_PATH = os.path.join(BASE_PATH, "search_prompt", "prompt.md") # Used in _get_system_prompt
DATABASE_CONTEXT_PATH = os.path.join(BASE_PATH, "search_prompt", "database_context.md") # Used in _get_system_prompt
OPTIMIZED_PROMPT_PATH = os.path.join(BASE_PATH, "search_prompt", "prompt_optimized.md") # Used in _get_system_prompt

class SQLiteAgent:
    def __init__(self):
        self.db_path = SQL_DATABASE_PATH
        self.db_uri = f"sqlite:///{self.db_path}"
        self.llm = LLM
        # Create SQLDatabase object from URI first
        self.db = SQLDatabase.from_uri(self.db_uri)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

    def _read_prompt_template(self, prompt_path: str, template_vars: dict = None) -> str:
            try: 
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                    if template_vars:
                        return template.format(**template_vars)   
                    return template
            except FileNotFoundError:
                raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")

    def _get_system_prompt(self):
        """Get comprehensive system prompt with database context and SQL rules"""
        # client = Client(api_key=LANGSMITH_API_KEY)
        # prompt = client.pull_prompt("langchain-ai/sql-agent-system-prompt", include_model=False)
        # system_message = prompt.format(dialect="SQLite", top_k=5)
        # return system_message
        current_date = datetime.now().strftime("%Y-%m-%d")
        database_context = self._read_prompt_template(DATABASE_CONTEXT_PATH)
        search_prompt = self._read_prompt_template(SEARCH_PROMPT_PATH, {"database_context": database_context, "current_date": current_date})
        return search_prompt

    def _clean_csv_files(self, user_id: str):
        csv_dir = f"{CSV_PATH}/{user_id}"
        os.makedirs(csv_dir, exist_ok=True)

        # Clean up old CSV files (keep only last 5)
        csv_files = [
            f
            for f in os.listdir(csv_dir)
            if f.startswith("data_") and f.endswith(".csv")
        ]
        csv_files.sort(reverse=True)  # Newest first
        for old_file in csv_files[5:]:  # Keep only 5 most recent
            os.remove(os.path.join(csv_dir, old_file))

# ==================================== Tools ==============================================
    def _get_country_airport_tool(self):
        def get_country_airport_code(
            country: Annotated[str, "Country name in Traditional Chinese (e.g., '日本', '韓國', '中國', '台灣')"]
        ):
            """
            Get all IATA airport codes for a specific country.
            
            Args:
                country: Country name in Traditional Chinese
                
            Returns:
                List of IATA airport codes for the specified country
            """
            try:
                # Load the airport mapping JSON file
                json_path = AIRPORT_MAPPING_PATH
                
                with open(json_path, 'r', encoding='utf-8') as file:
                    airports = json.load(file)
                
                # Filter airports by country
                country_airports = [
                    airport["IATA"] 
                    for airport in airports 
                    if airport["Country"] == country
                ]
                
                return country_airports
                
            except FileNotFoundError:
                return []
            except Exception as e:
                print(f"Error reading airport data: {e}")
                return []

                
        country_airport_code_description = (
            "Retrieve IATA airport codes for airports located in a specified country. "
            "This tool helps identify all airports within a country for database queries. "
            "Input: Country name in Traditional Chinese (e.g., '日本', '韓國', '中國', '台灣'). "
            "Output: Array of IATA codes (e.g., ['NRT', 'HND', 'KIX'] for Japan). "
            "Use this tool when users request data about flights to/from specific countries. "
            "The returned codes can be used in SQL WHERE clauses to filter by country."
        )
        country_airport_code_tool = Tool(
            name="get_country_airport_code",
            description=country_airport_code_description,
            func=get_country_airport_code,)
        return country_airport_code_tool

    def _get_csv_export_tool(self):
        def query_and_export_csv(
            query: Annotated[str, "The actual SQL query string to execute (e.g., 'SELECT * FROM flights WHERE...'). NOT the query result."],
            config: Annotated[RunnableConfig, InjectedToolArg]
        ) -> str:
            """
            Execute SQL query and automatically export results to CSV file.
            
            Args:
                query: The actual SQL query string to execute (e.g., 'SELECT * FROM flights WHERE destination = "Tokyo"').
                       This should be the SQL statement itself, NOT the result or output of a query.
                
            Returns:
                S3 URL of the exported CSV file
            """
            # Extract user_id from config's thread_id
            user_id = config.get("configurable", {}).get("thread_id", "default")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # Include milliseconds (YYYYMMDD_HHMMSS_mmm)
            csv_path = f"{CSV_PATH}/{user_id}/data_{timestamp}.csv"

            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(query, conn)
                conn.close()

                if df.empty:
                    return "Query executed successfully, but returned no data"

                # Create directory and save CSV
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                df.to_csv(csv_path, index=False)

                # Clean CSV path
                self._clean_csv_files(user_id)

                # Upload CSV file to S3
                s3_csv_url = s3_csv_uploader.upload_csv_file(csv_path, user_id)
                if s3_csv_url is None:
                    return "Error: Failed to upload CSV file to S3"
                
                return f"S3 CSV URL generated:\n {s3_csv_url}"

            except Exception as e:
                return f"Error: {e}"
        csv_export_tool_description = (
            "Input to this tool is a detailed and correct SQL query, output is a "
            "result from the database exported to CSV file. "
            "If the query is not correct, an error message will be returned. "
            "If an error is returned, rewrite the query, check the query, and try again. "
            "If you encounter an issue with Unknown column 'xxxx' in 'field list', "
            "use 'sql_db_schema' to query the correct table fields. "
            "This tool saves results to CSV file and uploads to S3."
            "Only use this tool when the user requests to export the results to CSV file."
        )
        csv_export_tool = Tool(
            name="sql_query_with_csv_export",
            description=csv_export_tool_description,
            func=query_and_export_csv,
        )
        return csv_export_tool

    def _get_tools(self):
        base_tools = self.toolkit.get_tools()
        csv_export_tool = self._get_csv_export_tool()  # No user_id needed - runtime extraction
        country_airport_code_tool = self._get_country_airport_tool()
        # Return base tools plus CSV export tool
        return base_tools + [csv_export_tool, country_airport_code_tool]
        
# ==================================== Agent (For STANDALONE purposes) ==============================================
    
    async def create_sql_agent(self):
        checkpointer = await get_shared_checkpointer()
        tools = self._get_tools()
        agent_graph = create_react_agent(
            self.llm,
            tools,
            prompt=self._get_system_prompt()
        )
        # Compile with checkpointer
        agent = agent_graph.compile(checkpointer=checkpointer)
        return agent
    
    async def invoke_sql_agent(self, user_id: str, message: str):
        agent = await self.create_sql_agent()
        response = await agent.ainvoke({"messages": [HumanMessage(content=message)]}, config={"configurable": {"thread_id": user_id}})
        return response["messages"][-1].content


async def main():
    sqlite_agent = SQLiteAgent()
    user_id = "1"
    
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() == "exit":
            break
        
        response = await sqlite_agent.invoke_sql_agent(user_id, user_input)
        print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
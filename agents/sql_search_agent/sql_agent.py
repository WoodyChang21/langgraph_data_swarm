import os
import json
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Annotated
import logging
from langchain_core.tools import Tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from agents.llm_model import LLM

logger = logging.getLogger(__name__)
load_dotenv()

SQL_DATABASE_PATH = os.getenv("SQL_DATABASE_PATH")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# PATHS
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_PATH, "csv") # Used in _get_csv_export_tool
AIRPORT_MAPPING_PATH = os.path.join(BASE_PATH, "airport_airline_mapping", "airport.json") # Used in _get_location_airport_tool
AIRLINE_MAPPING_PATH = os.path.join(BASE_PATH, "airport_airline_mapping", "airline.json") # Used in _get_location_airline_tool
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
    def _get_location_airport_tool(self):
        def get_location_airport_code(
            location: Annotated[
                str,
                (
                    "ALWAYS EXTRACT THE MOST SPECIFIC LOCATION MENTIONED. "
                    "Priority order → Airport name > City > Country. "
                    "From '泰國曼谷的廊曼機場', USE '廊曼'. "
                    "From '日本東京', USE '東京'. "
                    "From '泰國', USE '泰國'. "
                    "Do NOT include multiple levels — choose only the lowest-level (most specific) location."
                ),
            ]
        ):
            """
            Get IATA codes for a location. Always use the MOST SPECIFIC location mentioned.
            
            Args:
                location: Most specific location from user query
                
            Returns:
                List of IATA codes matching the location specificity
            """
            try:
                # Load the airport mapping JSON file
                json_path = AIRPORT_MAPPING_PATH
                
                with open(json_path, 'r', encoding='utf-8') as file:
                    airports = json.load(file)
                
                
                # First, try to match by city name (BN field)
                # Use partial matching to handle cities with multiple airports (e.g., '東京/成田', '東京/羽田')
                city_airports = [
                    airport["IATA"] 
                    for airport in airports 
                    if location in airport["BN"]  # Partial match for city names
                ]
                
                # If city match found, return those airports
                if city_airports:
                    return city_airports
                
                # Otherwise, try to match by country
                country_airports = [
                    airport["IATA"] 
                    for airport in airports 
                    if airport["Country"] == location
                ]
                
                return country_airports
                
            except FileNotFoundError:
                return []
            except Exception as e:
                print(f"Error reading airport data: {e}")
                return []

                
        location_airport_code_description = (
            "Get IATA airport codes for a given location. "
            "ALWAYS use the MOST SPECIFIC location available: airport > city > country. "
            "If the query includes multiple levels, pick only the LOWEST-LEVEL one. "
            "Examples: '廊曼' → ['DMK'], '東京' → ['NRT', 'HND'], '日本' → all Japan airports. "
            "Useful for generating SQL filters or API responses requiring IATA codes."
        )
        location_airport_code_tool = Tool(
            name="get_location_airport_code",
            description=location_airport_code_description,
            func=get_location_airport_code,)
        return location_airport_code_tool

    def _get_airline_code_tool(self):
        def get_airline_code(
            airline: Annotated[
                str,
                (
                    "Chinese airline name to search (e.g., '長榮', '國泰', '中華航空'). "
                    "Use full or partial airline name in Traditional Chinese. "
                    "Examples: '長榮' matches '長榮航空', '國泰' matches '國泰航空'."
                ),
            ]
        ):
            """
            Get IATA airline code from Chinese airline name.
            
            Args:
                airline: Airline name in Traditional Chinese (full or partial)
                
            Returns:
                List of matching IATA airline codes
            """
            try:
                # Load the airline mapping JSON file
                json_path = AIRLINE_MAPPING_PATH
                
                with open(json_path, 'r', encoding='utf-8') as file:
                    airlines = json.load(file)
                
                # Use partial matching to handle both full and abbreviated names
                matched_airlines = [
                    airline_data["IATA"]
                    for airline_data in airlines
                    if airline in airline_data["ChineseName"]  # Partial match
                ]
                
                return matched_airlines
                
            except FileNotFoundError:
                return []
            except Exception as e:
                print(f"Error reading airline data: {e}")
                return []
        
        airline_code_description = (
            "Get IATA airline codes from Chinese airline names. "
            "Supports full or partial names (e.g., '長榮' or '長榮航空' both work). "
            "Examples: '長榮' → ['BR'], '國泰' → ['CX'], '中華航空' → ['CI']. "
            "Use returned codes in SQL queries or direct responses."
        )
        
        airline_code_tool = Tool(
            name="get_airline_code",
            description=airline_code_description,
            func=get_airline_code,
        )
        return airline_code_tool
        
    def _get_airline_name_tool(self):
        def get_airline_name(
            iata_code: Annotated[str, "IATA airline code (e.g., 'BR', 'CI', 'CX')"]
        ):
            """
            Get airline Chinese name from IATA code.
            
            Args:
                iata_code: IATA airline code
                
            Returns:
                Chinese airline name or code if not found
            """
            try:
                with open(AIRLINE_MAPPING_PATH, 'r', encoding='utf-8') as file:
                    airlines = json.load(file)
                
                for airline in airlines:
                    if airline["IATA"] == iata_code:
                        return airline["ChineseName"]
                
                return iata_code  # Return code if not found
                
            except Exception as e:
                return iata_code
        
        airline_name_description = (
            "Get airline Chinese name from IATA code. "
            "Use this to display readable airline names in responses. "
            "Examples: 'BR' → '長榮航空', 'CI' → '中華航空', 'CX' → '國泰航空'."
        )
        
        return Tool(
            name="get_airline_name",
            description=airline_name_description,
            func=get_airline_name,
        )

    def _get_airport_name_tool(self):
        def get_airport_name(
            iata_code: Annotated[str, "IATA airport code (e.g., 'NRT', 'HND', 'ICN')"]
        ):
            """
            Get airport city/name from IATA code.
            
            Args:
                iata_code: IATA airport code
                
            Returns:
                Airport city name or code if not found
            """
            try:
                with open(AIRPORT_MAPPING_PATH, 'r', encoding='utf-8') as file:
                    airports = json.load(file)
                
                for airport in airports:
                    if airport["IATA"] == iata_code:
                        return f"{airport['BN']} ({airport['Country']})"
                
                return iata_code  # Return code if not found
                
            except Exception as e:
                return iata_code
        
        airport_name_description = (
            "Get airport city/name from IATA code. "
            "Use this to display readable airport names in responses. "
            "Examples: 'NRT' → '東京/成田 (日本)', 'ICN' → '仁川 (韓國)'."
        )
        
        return Tool(
            name="get_airport_name",
            description=airport_name_description,
            func=get_airport_name,
        )

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
                Local CSV file path
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
                filename = f"data_{timestamp}.csv"
                local_file_path = f"http://localhost:8080/sql_search_agent/csv/{user_id}/{filename}"

                # Clean CSV path
                self._clean_csv_files(user_id)

                return f"""✅ CSV exported successfully!

📥 **CSV URL:** {local_file_path}

💡 **For Handoffs:** When transferring to Analysis Agent or Plot Agent, use this URL:
   {csv_path}

When you transfer to Analysis Agent or Plot Agent, you should use {csv_path} as the CSV path.
"""

            except Exception as e:
                return f"Error: {e}"
        
        csv_export_tool_description = (
            "Input to this tool is a detailed and correct SQL query, output is a "
            "result from the database exported to CSV file. "
            "If the query is not correct, an error message will be returned. "
            "If an error is returned, rewrite the query, check the query, and try again. "
            "If you encounter an issue with Unknown column 'xxxx' in 'field list', "
            "use 'sql_db_schema' to query the correct table fields. "
            "This tool saves results to CSV file and returns the local CSV file path."
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
        location_airport_code_tool = self._get_location_airport_tool()
        airline_code_tool = self._get_airline_code_tool()
        airline_name_tool = self._get_airline_name_tool()
        airport_name_tool = self._get_airport_name_tool()
        extend_tools = [
            csv_export_tool, 
            location_airport_code_tool, 
            airline_code_tool, 
            airline_name_tool, 
            airport_name_tool]
        # Return base tools plus CSV export tool and location lookup tool
        return base_tools + extend_tools
        
# ==================================== Agent (For STANDALONE purposes) ==============================================
    
    async def create_sql_agent(self):
        tools = self._get_tools()
        agent = create_react_agent(
            self.llm,
            tools,
            prompt=self._get_system_prompt(),
        )
        return agent
    
    async def invoke_sql_agent(self, user_id: str, message: str):
        agent = await self.create_sql_agent()
        response = await agent.ainvoke({"messages": [HumanMessage(content=message)]}, config={"configurable": {"thread_id": user_id}})
        return response["messages"][-1].content


# async def main():
#     sqlite_agent = SQLiteAgent()
#     user_id = "1"
    
#     while True:
#         user_input = input("Enter your question: ")
#         if user_input.lower() == "exit":
#             break
#         if user_input.lower() == "clear history":
#         #     from agents.memory.memory_manager import clear_thread
#         #     await clear_thread(user_id)
#         #     print(f"History cleared for {user_id}")
#         #     continue
    
#         # response = await sqlite_agent.invoke_sql_agent(user_id, user_input)
#         print(response)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
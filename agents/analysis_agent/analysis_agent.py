from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_experimental.tools.python.tool import PythonAstREPLTool  # ← Changed!
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import Tool

from dotenv import load_dotenv
import os

from agents.llm_model import LLM

load_dotenv()

# Plot output path
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

class AnalysisAgent:
    def __init__(self):
        self.llm = LLM


# ==================================== Tools ==============================================
    def python_repl_tool(self):
        """Create Python AST REPL tool - returns last expression value"""
        repl_tool = PythonAstREPLTool(
            name="python_repl",
            description=(
                "A Python shell for data analysis. Execute python/pandas commands. "
                "The last line is automatically evaluated and returned (no print() needed). "
                "For multiple outputs, use print() statements."
            ),
            globals={},
            locals={}
        )
        return repl_tool

    def _get_tools(self):
        return [self.python_repl_tool()]

# ==================================== System Prompt ==============================================
    def _get_system_prompt(self):
        with open(os.path.join(BASE_PATH, "analysis_prompt", "analysis_prompt.md"), "r") as file:
            return file.read()

# ==================================== Agent ==============================================
    
    async def create_analysis_agent(self):
        tools = self._get_tools()
        checkpointer = InMemorySaver()
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=self._get_system_prompt(),
            checkpointer=checkpointer,
            debug=True
        )
        return agent
    
    async def invoke_analysis_agent(self, user_id: str, message: str):
        """Invoke the plot agent with a message"""
        agent = await self.create_analysis_agent()
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": user_id}}
        )
        return response["messages"][-1].content

analysis_agent = AnalysisAgent()
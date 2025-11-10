import re
from dataclasses import is_dataclass
from typing import Annotated, Any, Dict

from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import InjectedState, ToolNode
from langgraph.types import Command, Send

from pydantic import BaseModel

WHITESPACE_RE = re.compile(r"\s+")
METADATA_KEY_HANDOFF_DESTINATION = "__handoff_destination"

def _get_field(obj: Any, key: str) -> Any:
    """Get a field from an object.

    This function retrieves a field from a dictionary, dataclass, or Pydantic model.

    Args:
        obj: The object from which to retrieve the field.
        key: The key or attribute name of the field to retrieve.

    Returns:
        The value of the specified field.

    """
    if isinstance(obj, dict):
        return obj[key]
    if is_dataclass(obj) or isinstance(obj, BaseModel):
        return getattr(obj, key)
    msg = f"Unsupported type for state: {type(obj)}"
    raise TypeError(msg)

def _normalize_agent_name(agent_name: str) -> str:
    """Normalize an agent name to be used inside the tool name."""
    return WHITESPACE_RE.sub("_", agent_name.strip()).lower()


def create_task_description_handoff_tool(
    *, 
    agent_name: str, 
    name: str | None = None, 
    description: str | None = None
):
    name = name or f"transfer_to_{_normalize_agent_name(agent_name)}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_to_agent(
        # this is populated by the supervisor LLM
        task_description: Annotated[
            str,
            "Detailed instruction and goal for the next agent to achieve",
        ],
        # these parameters are ignored by the LLM
        state: Annotated[Dict[str, Any], InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        
        # task_description_message = ("user", task_description)
        tool_message = ToolMessage(
            content=f"[Transferring to {agent_name}]\n\n{task_description}",
            name=f"{name}",
            tool_call_id=tool_call_id,
        )
    
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": [*_get_field(state, "messages"), tool_message],
                "active_agent": agent_name,
            },
        )

    handoff_to_agent.metadata = {METADATA_KEY_HANDOFF_DESTINATION: agent_name}
    return handoff_to_agent
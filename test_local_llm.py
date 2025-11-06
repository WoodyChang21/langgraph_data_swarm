from langchain.agents import create_react_agent
from langchain_core.messages import HumanMessage
from agents.llm_model import LLM

chat_history = []

def invoke_agent(user_input: str):
    user_messages = [HumanMessage(content=user_input)]
    chat_history.extend(user_messages)
    ai_message = LLM.invoke(chat_history)
    chat_history.append(ai_message)

    return ai_message.content

def check_llm():
    print(f"LLM: {LLM.model}")

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        response = invoke_agent(user_input)
        print(f"AI: {response}")
    # check_llm()
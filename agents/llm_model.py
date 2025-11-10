from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()

LOCAL_MODEL = False

if LOCAL_MODEL:
    # Use Docker network gateway - container network gateway is 192.168.16.1
    LLM = ChatOllama(model="qwen3:8b", temperature=0.1, max_tokens=1000, timeout=30, base_url="http://192.168.16.1:11434")
else:
    LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000, timeout=30)

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()

LOCAL_MODEL = False

if LOCAL_MODEL:
    # Use Docker network gateway - container network gateway is 172.25.0.1
    LLM = ChatOllama(model="qwen3:8b", reasoning = False, temperature=0.1, max_tokens=1000, timeout=30, base_url="http://host.docker.internal:11434" )
    # LLM = ChatOllama(model="qwen3:14b", reasoning=False, temperature=0.1, max_tokens=1000, timeout=30, base_url="http://host.docker.internal:11434" )
    # LLM = ChatOllama(model="gpt-oss:20b", reasoning=True, temperature=0.1, max_tokens=1000, timeout=30, base_url="http://host.docker.internal:11434" )
    # LLM = ChatOllama(model="granite4:7b-a1b-h", temperature=0.1, max_tokens=1000, timeout=30, base_url="http://host.docker.internal:11434" )
    # LLM = ChatOllama(model="llama3.2:3b-instruct-q8_0", temperature=0.1, max_tokens=1000, timeout=30, base_url="http://host.docker.internal:11434" )
else:
    LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000, timeout=30)

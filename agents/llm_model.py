from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()


# Load the model for the entire project
LOCAL_MODEL = False  # Set to True for Ollama, False for OpenAI
# Ollama base URL - use host.docker.internal when running in Docker
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

if LOCAL_MODEL:
    LLM = ChatOllama(
        model="qwen3-coder:latest",
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
        base_url=OLLAMA_BASE_URL
    )
else:
    LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000, timeout=30)

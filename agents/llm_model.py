from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()


# Load the model for the entire project
LOCAL_MODEL = False  # Set to True for Ollama, False for OpenAI

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
# OLLAMA_MODEL = "qwen3-coder:latest"
# OLLAMA_MODEL = "llama3.1:latest"
OLLAMA_MODEL = "qwen3:8b"


if LOCAL_MODEL:
    LLM = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
        base_url=OLLAMA_BASE_URL
    )
else:
    LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000, timeout=30)

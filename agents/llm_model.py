from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()

LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000, timeout=30)

# Ollama -> llama3
import os
from langchain_ollama import ChatOllama  

MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_llm():
    return ChatOllama(model=MODEL_NAME, base_url=BASE_URL, temperature=0.2)

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLM:
    def __init__(self, model_name="openai/gpt-oss-120b"):
        self.llm = ChatGroq(
            api_key = GROQ_API_KEY,
            model = model_name,
            temperature = 0.0,
            max_tokens = 1024
        )

    def invoke(self, prompt):
        response = self.llm.invoke(prompt)
        return response.content
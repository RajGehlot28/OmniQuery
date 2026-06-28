from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LLM:
    def __init__(self, model_name="gpt-4o-mini"):
        self.llm = ChatOpenAI(
            api_key = OPENAI_API_KEY,
            model = model_name,
            temperature = 0.0,
            max_tokens = 1024
        )

    async def invoke(self, prompt):
        response = await self.llm.ainvoke(prompt) # asynchronous invoke method call
        return response.content

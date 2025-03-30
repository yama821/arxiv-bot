from openai import OpenAI
import os

class LLMClient:
    def __init__(self):
        # openai.api_key = os.environ["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def chat_completion(self, messages, model='gpt-4o-mini', max_tokens=1000, temperature=0.7):
        response = self.client.responses.create(
            model=model,
            input=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.output_text

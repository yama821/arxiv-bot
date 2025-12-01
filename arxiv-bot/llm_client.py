from openai import OpenAI
import os
from pathlib import Path
import asyncio

class LLMClient:
    def __init__(self):
        # openai.api_key = os.environ["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.used_input_tokens = 0
        self.used_output_tokens = 0

    def chat_completion(self, messages, model='gpt-5-mini'):
        response = self.client.responses.create(
            model=model,
            input=messages,
        )
        self.used_input_tokens += response.usage.input_tokens
        self.used_output_tokens += response.usage.output_tokens
        return response.output_text

    async def chat_completion_async(self, messages, model='gpt-5-mini'):
        return await asyncio.to_thread(
            lambda: self.chat_completion(messages, model)
        )
    
    
    def summarize_math_paper(self, paper_text, to_async = False):
        prompt_path = Path(__file__).resolve().parent / "prompts/summarize_math_paper.txt"
        with open(prompt_path) as f:
            system_prompt = f.read()
        
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": paper_text},
        ]

        if to_async:
            ret = self.chat_completion_async(prompt)
        else:
            ret = self.chat_completion(prompt)
        return ret
    
    def generate_with_system_prompt(self, prompt_type, input_text, to_async = False):
        prompt_path = Path(__file__).resolve().parent / f"prompts/{prompt_type}.txt"
        with open(prompt_path) as f:
            system_prompt = f.read()

        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
        ]

        if to_async:
            ret = self.chat_completion_async(prompt)
        else:
            ret = self.chat_completion(prompt)
        return ret

if __name__ == "__main__":
    file_name = input()
    paper_path = Path(__file__).resolve().parent.parent / f"data/{file_name}"
    with open(paper_path, encoding='utf-8', errors='replace') as f:
        paper = f.read()

    client = LLMClient()
    ret = client.summarize_math_paper(paper)
    print(ret)

from openai import OpenAI
import os
from pathlib import Path

class LLMClient:
    def __init__(self):
        # openai.api_key = os.environ["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def chat_completion(self, messages, model='gpt-4o-mini', temperature=0.7):
        response = self.client.responses.create(
            model=model,
            input=messages,
            temperature=temperature,
        )
        return response.output_text
    
    def summarize_math_paper(self, paper_text):
        prompt_path = Path(__file__).resolve().parent / "prompt.txt"
        with open(prompt_path) as f:
            system_prompt = f.read()
        
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": paper_text},
        ]

        ret = self.chat_completion(prompt, temperature=0.0)
        return ret

if __name__ == "__main__":
    file_name = input()
    paper_path = Path(__file__).resolve().parent.parent / f"data/{file_name}"
    with open(paper_path, encoding='utf-8', errors='replace') as f:
        paper = f.read()

    client = LLMClient()
    ret = client.summarize_math_paper(paper)
    print(ret)

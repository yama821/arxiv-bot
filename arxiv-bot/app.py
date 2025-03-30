from llm_client import LLMClient
from pathlib import Path

client = LLMClient()

prompt_path = Path(__file__).resolve().parent / "prompt.txt"
with open(prompt_path) as f:
    system_prompt = f.read()

file_name = input()
paper_path = Path(__file__).resolve().parent.parent / f"data/{file_name}"
with open(paper_path, encoding='utf-8', errors='replace') as f:
    paper = f.read()

prompt = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": paper},
]

ret = client.chat_completion(prompt)
print(ret)

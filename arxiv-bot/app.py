from llm_client import LLMClient
from ocr import MistralOCR

if __name__ == "__main__":
    paper_url = "https://arxiv.org/pdf/2503.21077"

    ocr_client = MistralOCR()
    paper_text = ocr_client.render_md(paper_url)

    llm_client = LLMClient()
    summary = llm_client.summarize_math_paper(paper_text)

    print(summary)

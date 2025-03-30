from llm_client import LLMClient
from ocr import MistralOCR
from search import ArxivClient

if __name__ == "__main__":

    query = "combinatorics"
    arxiv_client = ArxivClient()
    search_results = arxiv_client.search(query)
    top_result = search_results[0]

    abst = top_result.summary

    llm_client = LLMClient()
    summary = llm_client.generate_with_system_prompt('translate_abstruct', abst)
    print(summary)


    # paper_url = "https://arxiv.org/pdf/2503.21077"
    # ocr_client = MistralOCR()
    # paper_text = ocr_client.render_md(paper_url)

    # llm_client = LLMClient()
    # summary = llm_client.summarize_math_paper(paper_text)

    # print(summary)

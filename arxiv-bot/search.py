# search.py
import arxiv
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional


class ArxivClient:
    """
    arxiv ライブラリの薄いラッパ。
    - arXiv ID から 1 件取得
    - URL (abs / pdf) から ID を抜いて 1 件取得
    - arxiv.Result → dict 変換
    """

    def __init__(self) -> None:
        self.client = arxiv.Client()

    # ---- 基本検索（クエリから複数件） ----

    def search(self, query: str, max_results: int = 5) -> List[arxiv.Result]:
        search_state = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        results = list(self.client.results(search_state))
        return results

    # ---- arXiv ID / URL から 1 件取得 ----

    def get_result_by_id(self, arxiv_id: str) -> arxiv.Result:
        search_state = arxiv.Search(id_list=[arxiv_id])
        results = list(self.client.results(search_state))
        if not results:
            raise ValueError(f"No arXiv result found for id: {arxiv_id}")
        return results[0]

    def parse_id_from_url(self, url: str) -> Optional[str]:
        """
        arXiv の abs / pdf URL から arXiv ID を取り出す。
          https://arxiv.org/abs/2411.01234      -> 2411.01234
          https://arxiv.org/pdf/2411.01234.pdf -> 2411.01234
        """
        parsed = urlparse(url)
        if "arxiv.org" not in parsed.netloc:
            return None

        path = parsed.path.strip("/")
        parts = path.split("/")
        if not parts:
            return None

        last = parts[-1]
        if last.lower().endswith(".pdf"):
            last = last[:-4]

        return last or None

    def get_result_from_url(self, url: str) -> arxiv.Result:
        """
        abs / pdf どちらを渡しても OK。
        URL から ID を抜き出し、その ID で 1 件取得する。
        """
        arxiv_id = self.parse_id_from_url(url)
        if arxiv_id is None:
            raise ValueError(f"Not a valid arXiv URL: {url}")
        return self.get_result_by_id(arxiv_id)

    # ---- arxiv.Result → dict 変換 ----

    def result_to_dict(self, result: arxiv.Result) -> Dict[str, Any]:
        """
        app.py のパイプラインが期待している dict 形式に変換する。
        keys:
          - title
          - abs_url
          - pdf_url
          - primary_subject
          - published (datetime)
          - authors (str)
          - abstract (str)
        """
        abs_url = result.entry_id
        pdf_url = result.pdf_url

        # primary_category は python-arxiv の属性をそのまま使う
        primary_subject: str
        if getattr(result, "primary_category", None):
            primary_subject = str(result.primary_category)
        elif getattr(result, "categories", None):
            primary_subject = result.categories[0]
        else:
            primary_subject = "unknown"

        authors = ", ".join([a.name for a in result.authors])
        published = result.published
        abstract = result.summary

        return {
            "title": result.title,
            "abs_url": abs_url,
            "pdf_url": pdf_url,
            "primary_subject": primary_subject,
            "published": published,
            "authors": authors,
            "abstract": abstract,
        }

    def get_metadata_from_url(self, url: str) -> Dict[str, Any]:
        """
        abs / pdf URL を渡すと、パイプラインでそのまま使える dict を返す。
        """
        result = self.get_result_from_url(url)
        return self.result_to_dict(result)

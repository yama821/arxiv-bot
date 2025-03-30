import arxiv

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search(self, query) -> list[arxiv.Result]:
        search_state = arxiv.Search(
            query = query,
            max_results = 5,
            sort_by = arxiv.SortCriterion.LastUpdatedDate,
        )

        results = self.client.results(search_state)
        results = [result for result in results]
        return results

import arxiv

# https://github.com/lukasschwab/arxiv.py

class UseCases:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_by_query(self, query, max_results = 3):
        search = arxiv.Search(
            query = "combinatorics",
            max_results = max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        results = self.client.results(search)
        return results

    def search_by_id(self, id):
       search = arxiv.Search(id_list = [id])
       result = next(self.client.results(search))
       return result
    
    def search_by_ids(self, ids):
       search = arxiv.Search(id_list = ids)
       results = self.client.results(search)
       return results
    
usecase = UseCases()
paper = usecase.search_by_id("2309.01119")
print(paper.summary)

paper.download_pdf(dirpath=".", filename="test-paper.pdf")
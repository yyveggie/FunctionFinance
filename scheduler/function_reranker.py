import rootutils 
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import inspect
from flashrank import Ranker, RerankRequest
from typing import List, Callable

top_k = 5

class RerankerFunctions:
    def __init__(self, query, functions: List[Callable]):
        self.query = query
        self.functions = functions
        self.top_k = top_k

    async def __call__(self):
        return await self.rerank(self.query)

    async def rerank(self, query: str) -> List[Callable]:
        cache_dir = "~/flashrank_models"  # 在家目录下创建一个文件夹
        ranker = Ranker(model_name="rank-T5-flan", cache_dir=cache_dir)

        passages = []
        for i, func in enumerate(self.functions, start=1):
            function_info = f"Index: {i}\n"
            function_info += f"Function Name: {func.__name__}\n"
            function_info += f"Documentation: {inspect.getdoc(func)}\n" if inspect.getdoc(func) else ""
            passages.append({"id": i, "text": function_info})

        rerankrequest = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(rerankrequest)

        reranked_functions = [self.functions[result["id"] - 1] for result in results[:self.top_k]]
        return reranked_functions

async def run(query, functions):
    parser = RerankerFunctions(query, functions)
    return await parser()
class SubqueryPrediction(BaseModel):
    """
    Class for subquery label predictions.
    """
    subqueries: List[str] = Field(..., description="The input subqueries, in the same order as provided.")
    search_keywords: List[List[str]] = Field(..., description="The extracted search_keywords from the original query.") 
    
    def __init__(self, **data):
        super().__init__(**data)
        lengths = [len(data["subqueries"]), len(data["search_keywords"])]
        if len(set(lengths)) > 1:
            raise ValueError("Lengths of subqueries and search keywords must be equal.")

class DataDownloadr:
    def __init__(self, search_keyword):
        self.search_keyword = search_keyword
        self.functions_calling_path = './apis/'

    async def __call__(self):
        return await self.function_calling(self.search_keyword)
    
    async def query_rewriter(self, query: str):
        today = datetime.now().strftime("%Y-%m-%d")
        response = await client_classify.chat.completions.create(
            model=GPT4O,
            response_model=SubqueryPrediction,
            max_retries=3,
            messages=[
                {
                    "role": "system",
                    "content": dedent(
                        f"""
                        As an intelligent financial task allocator, my role is to receive the original query from the user, break it down into appropriate subqueries, and then perform the remaining tasks for each subquery. This involves selecting the appropriate method to obtain the required financial data based on the subquery content and providing an accurate response.
                        For each subquery that I generate, I will comprehensively consider the following points:

                        The specific content and granularity of the subquery
                        The accuracy, timeliness, and ease of use of data obtained through different methods
                        Computational cost and time overhead of the subquery

                        My goal is to fulfill the user's financial data query needs in the most efficient and accurate manner, providing professional and reliable data services. I will return a response with two fields:

                        'subqueries': A list of the subqueries I generated from the original query.
                        'search_keywords': A list of search keywords extracted from each subquery, to make the subquery more suitable for search engines. The search keywords should correspond to the subqueries in the correct order.

                        When rewriting 'search_keywords', I MUST pay special attention to time-sensitive information and include relevant dates. Today's date is {today}.
                        
                        For example:
                        Original query: 'What is Tesla's current stock price and its historical price data? Also get me today's major world news and Apple's 2022 financial statements.'
                        Output:

                        'subqueries': ['What is the current stock price of Tesla?', 'What is the historical price data of Tesla stock', 'What are the major world news today?', 'Show me the financial statements of Apple in 2022']
                        'search_keywords': [['Tesla', 'stock price', 'current', '{today}'], ['Tesla', 'stock', 'historical price data'], ['world', 'news', '{today}'], ['Apple', 'financial statements', 'year 2022']]
                        
                        Take a deep breath, here is the original query: 
                        """
                    )
                    },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )  # type: ignore
        return response
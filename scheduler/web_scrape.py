import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import requests
import asyncio
import os
from loguru import logger
from web_search import (
    embedding_rag, 
    google_search, 
    scrape_content,
    searxng_search
    )
from textwrap import dedent
from langchain.prompts import PromptTemplate
from config_loader import SEARCH_LEVEL

class QueryProcessor:
    def __init__(self):
        self.BING_SEARCH_V7_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
        self.GOOGLE_SEARCH_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
        self.BING_MKT = "en-US"
        self.DEFAULT_SEARCH_ENGINE_TIMEOUT = 5
        self.REFERENCE_NUM = 10
        self.subscription_key = os.getenv('BING_SEARCH_API_KEY')
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.GOOGLE_SEARCH_CX = os.getenv('GOOGLE_CSE_ID')
        self.summarize_template = dedent("""
            I am your assistant, dedicated to helping you fulfill user requests.
            
            The structure of the obtained data is usually presented as a list of dictionaries, where each dictionary represents a piece of data with the keys "context" and "url", or "value"(if any).

            Write an accurate and detailed answer for the given question using only the provided data. Incorporating the relevant information into the answer and cite the corresponding data source using the format [x], where x is the index of the data source (key 'url') in the provided list.

            You must only use information from the provided data. Use an unbiased and journalistic tone. 
            
            There may be expired data in the provided context, please pay attention to filtering. Today's date: {today}. 
            
            Combine the data together into a coherent answer. Do not repeat text.

            Cite the data sources in the appropriate parts of the answer using the [x] format.

            After your response, you MUST provide the sources you used in the following format:

            [Your Response]

            Sources:

            [1] Source 1 URL

            [2] Source 2 URL

            ...

            The sources should be listed in the order they appear in your response, with each source URL on a new line, preceded by its corresponding number in square brackets.

            Here is the obtained data:

            {contexts_and_urls}

            """)
        self.prompt = PromptTemplate(input_variables=["today", "contexts_and_urls"], template=self.summarize_template)

    async def search_with_bing(self, search_keywords: str):
        """ Search with bing and return the contexts. """
        result_list = []
        params = {"q": search_keywords, "mkt": self.BING_MKT}
        response = requests.get(
            self.BING_SEARCH_V7_ENDPOINT,
            headers={"Ocp-Apim-Subscription-Key": self.subscription_key},
            params=params,
            timeout=self.DEFAULT_SEARCH_ENGINE_TIMEOUT,
        )
        if not response.ok:
            logger.error(f"{response.status_code} {response.text}")
            return None
        json_content = response.json()
        try:
            search_items = json_content["webPages"]["value"][:self.REFERENCE_NUM]
        except KeyError:
            logger.error(f"Error encountered: {json_content}")
            return {"context": [], "url": []}
        for item in search_items:
            result_dict = {}
            result_dict["context"] = item["snippet"]
            result_dict["url"] = item["url"]
            result_list.append(result_dict)
        return result_list

    async def search_with_google(self, search_keywords: str):
        """ Search with google and return the contexts. """
        result_list = []
        params = {
            "key": self.google_search_api_key, 
            "cx": self.GOOGLE_SEARCH_CX,
            "q": search_keywords,
            "num": self.REFERENCE_NUM,
        }
        response = requests.get(
            self.GOOGLE_SEARCH_ENDPOINT,
            params=params, 
            timeout=self.DEFAULT_SEARCH_ENGINE_TIMEOUT
        )
        if not response.ok:
            logger.error(f"{response.status_code} {response.text}")
            return None
        json_content = response.json()
        try:
            search_items = json_content["items"][:self.REFERENCE_NUM]
        except KeyError:
            logger.error(f"Error encountered: {json_content}")
            return []
        for item in search_items:
            result_dict = {}
            if "htmlSnippet" in item: 
                html_snippet = item["htmlSnippet"]
            else: 
                html_snippet = ""
            if "snippet" in item: 
                snippet = item["snippet"]
            else: 
                snippet = ""
            result_dict["context"] = html_snippet + " " + snippet
            if "link" in item: 
                result_dict["url"] = item["link"]
            else: 
                result_dict["url"] = ""
            result_list.append(result_dict)
        return result_list

    async def __call__(self, search_keywords: str):
        try:
            contexts_and_urls = await self.search_with_google(search_keywords)
        except:
            contexts_and_urls = await self.search_with_bing(search_keywords)
        
        if SEARCH_LEVEL == '3':
            contexts_and_urls = await embedding_rag.run(urls=[item['url'] for item in contexts_and_urls], query=search_keywords)
        elif SEARCH_LEVEL == '2':
            contexts_and_urls = await scrape_content.run(urls=[item['url'] for item in contexts_and_urls])
        elif SEARCH_LEVEL == '1':
            contexts_and_urls = await searxng_search.run(search_keywords=search_keywords)
        
        return dedent(f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
</START>{contexts_and_urls}</END>
After your response, you MUST provide the sources you used in the following format:
[Your Response]
Sources:
[1] Source 1 URL
[2] Source 2 URL
""").strip()
        
async def run(search_keywords: str):
    parser = QueryProcessor()
    return await parser(search_keywords=search_keywords)

if __name__ == "__main__":
    search_keywords = "特斯拉 股价 2024-05-21"  
    print(asyncio.run(run(search_keywords)))
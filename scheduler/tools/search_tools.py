from langchain_community.tools.tavily_search import TavilySearchResults
from crewai_tools import (
    ScrapeWebsiteTool,
    ScrapeElementFromWebsiteTool
)
from langchain.tools import tool
from brave import Brave
import requests
import json
import os

Tavily_API_KEY = os.environ.get('TAVILY_API_KEY')
search_tool = TavilySearchResults()

scrape_website_tool = ScrapeWebsiteTool()
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
brave = Brave(api_key=BRAVE_API_KEY)

@tool('Brave Search')
def search(search_query: str):
    """Search the web for information on a given topic"""
    return brave.search(q=search_query, count=10)


class SearchTools():
    @tool("Search the internet")
    def search_internet(query):
        """Useful to search the internet 
        about a a given topic and return relevant results"""
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['organic']
        string = []
        for result in results[:top_result_to_return]:
            try:
                string.append('\n'.join([
                    f"Title: {result['title']}", f"Link: {result['link']}",
                    f"Snippet: {result['snippet']}", "\n-----------------"
                ]))
            except KeyError:
                next

        return '\n'.join(string)

    @tool("Search news on the internet")
    def search_news(query):
        """Useful to search news about a company, stock or any other
        topic and return relevant results"""""
        top_result_to_return = 4
        url = "https://google.serper.dev/news"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['news']
        string = []
        for result in results[:top_result_to_return]:
            try:
                string.append('\n'.join([
                    f"Title: {result['title']}", f"Link: {result['link']}",
                    f"Snippet: {result['snippet']}", "\n-----------------"
                ]))
            except KeyError:
                next

        return '\n'.join(string)


def tools():
    return [search_tool, search]

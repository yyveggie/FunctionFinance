import asyncio
from langchain_community.utilities.searx_search import SearxSearchWrapper

search = SearxSearchWrapper(searx_host="http://127.0.0.1:8080")

# print(search.run("latest apple price 2024-04-18", engines=['google', 'bing', 'duckduckgo'], categories='news', num_results=20))

async def get_results(search_keywords):
    return search.results(
        search_keywords,
        num_results=20,
        time_range="day",
        # engine=['bing'],
        # categories="news",
    )

async def run(search_keywords: str):
    output = []
    results = await get_results(search_keywords)
    print(results)
    for result in results:
        lines = result['snippet'].splitlines()
        context = ''.join(lines)
        output.append({
            'context': context,
            'url': result['link']
        })
    return output

async def main():
    import pprint
    results = await run("china")
    pprint.pprint(results)

if __name__ == '__main__':
    asyncio.run(main())
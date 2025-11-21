import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import asyncio
from embedchain import App
from config_loader import OPENAI_API_KEY
import logging

logging.getLogger("embedchain.vectorstores.local_persistent_hnsw").setLevel(logging.ERROR)

class EmbedChainTool:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        self.app = App()

    async def __call__(self, urls, query):
        await self.add_resources(urls)
        return await self.search(query)

    async def add_resources(self, urls):
        for url in urls:
            try:
                self.app.add(url)
            except Exception as e:
                logging.info(f"Error adding URL: {url}")
                logging.info(f"Error message: {str(e)}")
                continue

    async def query(self, question):
        return await asyncio.to_thread(self.app.query, question)

    async def search(self, question):
        results = await asyncio.to_thread(self.app.search, question, num_documents=5)
        simplified_results = []
        for result in results:
            simplified_result = {
                'context': result['context'],
                'url': result['metadata']['url']
            }
            simplified_results.append(simplified_result)
        return simplified_results

async def run(urls: list, query: str):
    parser = EmbedChainTool()
    return await parser(urls=urls, query=query)

async def main():
    import pprint
    query_tool = EmbedChainTool()
    urls = ['https://www.youtube.com/watch?v=GDXCdy5CMfc',
            'https://wng.org/podcasts/thursday-morning-news-april-18-2024-1713361501',
            'https://www.usnews.com/news/world/articles/2024-04-18/belgian-and-czech-leaders-exhort-the-eu-to-react-amid-concern-over-russian-election-interference',
            'https://www.nytimes.com/live/2024/04/18/world/iran-israel-gaza-war-news',
            'https://nypost.com/2024/04/18/world-news/indonesian-volcano-erupts-several-times-officials-fear-it-could-collapse-into-the-sea-as-tsunami-warning-issued/',
            'https://www.upi.com/Top_News/World-News/2024/04/18/UN-food-convoy-enters-Gaza/5821713430059/',
            'https://www.cnbc.com/2024/04/18/worlds-largest-sovereign-wealth-fund-posts-110-billion-in-q1-profit.html',
            'https://www.bloomberg.com/news/newsletters/2024-04-18/world-economy-latest-new-fed-outlook-leaves-world-edgy-on-currencies',
            'https://www.nytimes.com/live/2024/04/18/world/iran-israel-gaza-war-news',
            'https://www.usnews.com/news/world/articles/2024-04-18/belgian-and-czech-leaders-exhort-the-eu-to-react-amid-concern-over-russian-election-interference',
            'https://www.reuters.com/markets/us/global-markets-view-usa-2024-04-18/',
            'https://www.upi.com/Top_News/World-News/2024/04/18/UN-food-convoy-enters-Gaza/5821713430059/']
    await query_tool.add_resources(urls)
    question = "what are the big news today?"
    answer = await query_tool.search(question)
    pprint.pprint(answer)

if __name__ == "__main__":
    asyncio.run(main())
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    根据所选特征来筛选 IPO。
'''
import logging
import aiohttp
import asyncio
from crawler.screener.stockanalysisIPOScreener import StockAnalysis_IPO_Screener
from config import config
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class IPOScreenerCrawlerFunctions:
    def __init__(self):
        self.alldata = {}

    async def fetch_ipo_screener(self, source_name, crawler_class, session, rankingCategory):
        try:
            crawler = crawler_class(rankingCategory, config, session)
            data = await crawler.download()
            self.alldata[f"{source_name}_ipo_screener"] = {
                "Prompt": f"This is the ipo screener downloaded from the {source_name}.", "data": data}
        except Exception as e:
            logging.error("Error in %s_ipo_screener: %s", source_name, e)
            self.alldata[f"{source_name}_ipo_screener"] = f"Error in collecting data from {source_name}"

    async def run_in_parallel(self, rankingCategory):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_ipo_screener(
                    "stockanalysis", StockAnalysis_IPO_Screener, session, rankingCategory),
            ]
            await asyncio.gather(*tasks)

    def return_data(self):
        return self.alldata


async def main(rankingCategory):
    crawler = IPOScreenerCrawlerFunctions()
    await crawler.run_in_parallel(rankingCategory)
    data = crawler.return_data()
    print(data)

# if __name__ == '__main__':
#     asyncio.run(main())

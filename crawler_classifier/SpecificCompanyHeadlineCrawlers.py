import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定公司的头条，部分也会有摘要。
'''
from config import config
from crawler.headline.googlefinanceSpecificCompanyHeadline import Google_Finance_Specific_Company_Headline
from crawler.news.gurufocusSpecificCompanyNews import GuruFocus_Specific_Company_Headline
from crawler.news.seekingalphaSpecificCompanyNews import SeekingAlpha_Specific_Company_News
from crawler.news.stockanalysisSpecificCompanyNews import StockAnalysis_Specific_Company_News
from crawler.headline.finnhubSpecificCompanyHeadline import Finnhub_Specific_Company_Headline
from crawler.headline.yahooSpecificCompanyHeadline import Yahoo_Specific_Company_Headline
import json
import asyncio
import aiohttp
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanyHeadlineCrawlerFunctions:
    def __init__(self):
        self.alldata = {}

    async def fetch_headlines(self, source_name, crawler_class, session, ticker):
        try:
            crawler = crawler_class(ticker, config, session)
            data = await crawler.download()
            if not data.empty:
                self.alldata[f"{source_name}"] = data.to_dict(orient='records')
            else:
                self.alldata[f"{source_name}"] = 'None'
        except Exception as e:
            logging.error("Error in %s_headlines: %s", source_name, e)
            self.alldata[f"{source_name}"] = f"Error in collecting data from {source_name}"

    async def run_in_parallel(self, ticker):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_headlines(
                    "gurufocus", GuruFocus_Specific_Company_Headline, session, ticker),
                self.fetch_headlines(
                    "seekingalpha", SeekingAlpha_Specific_Company_Headline, session, ticker),
                self.fetch_headlines(
                    "stockanalysis", StockAnalysis_Specific_Company_Headline, session, ticker),
                self.fetch_headlines(
                    "finhub", Finnhub_Specific_Company_Headline, session, ticker),
                self.fetch_headlines(
                    "yahoo", Yahoo_Specific_Company_Headline, session, ticker)
            ]
            await asyncio.gather(*tasks)

    def return_data(self):
        return json.dumps(self.alldata)


async def main(ticker):
    crawler = SpecificCompanyHeadlineCrawlerFunctions()
    await crawler.run_in_parallel(ticker)
    data = crawler.return_data()
    return data

if __name__ == '__main__':
    data = asyncio.run(main('BABA'))
    print(data)

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from config import config
from crawler.ipocalendar.stockanalysisIPOCalendar import StockAnalysis_IPO_Calendar
import asyncio
import aiohttp
import logging
'''
    下载 IPO 日历: 包括本周 IPO, 下周 IPO, 下周之后的 IPO, 下载 IPO Filings 和 Withdrawn IPOs。
'''
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class IPOsCalendarCrawlerFunctions:
    def __init__(self):
        self.alldata = {}

    async def fetch_ipo_data(self, session):
        stockanalysis = StockAnalysis_IPO_Calendar(config, session)
        try:
            self.alldata["upcoming_ipos"] = await stockanalysis.download_upcoming_ipos()
        except Exception as e:
            logging.error("Error in StockAnalysis upcoming_ipos: %s", e)
        try:
            self.alldata["filings"] = await stockanalysis.download_filings()
        except Exception as e:
            logging.error("Error in StockAnalysis filings: %s", e)
        try:
            self.alldata["withdrawn"] = await stockanalysis.download_withdrawn()
        except Exception as e:
            logging.error("Error in StockAnalysis withdrawn: %s", e)

    async def run_in_parallel(self):
        async with aiohttp.ClientSession() as session:
            await self.fetch_ipo_data(session)

    def return_data(self):
        return self.alldata


async def main():
    crawler = IPOsCalendarCrawlerFunctions()
    await crawler.run_in_parallel()
    return crawler.return_data()

if __name__ == '__main__':
    data = asyncio.run(main())
    print(data)

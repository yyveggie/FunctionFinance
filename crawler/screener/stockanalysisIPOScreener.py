import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 根据所选特征来筛选 ipo，但只能通过一个特征来筛选。
    注意：这个筛选机制还不是很清楚，有时间检查一下。
'''
import asyncio
import aiohttp
import json
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent


class StockAnalysis_IPO_Screener(Usable_IP):
    def __init__(self, rankingCategory, args={}, session=None):
        super().__init__(args)
        self.session = session
        # self.rankingCategory = args["ranking_category"][0]
        self.rankingCategory = rankingCategory
        self.db_connection = AsyncMongoConnection('IPO_Screener')
        self.source = "stockanalysis"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    async def download(self):
        url = f"https://stockanalysis.com/api/screener/i/bd/{self.rankingCategory}.json"
        try:
            response_text = await self.request_get(session=self.session, url=url, headers=self.headers)
            if response_text:
                data_dict = json.loads(response_text)['data']
                await self.db_connection.save_data(self.rankingCategory, self.source, data_dict)
                return data_dict
            else:
                return f'Current {self.rankingCategory} does not support to screener the IPO, please change one.'
        except Exception as e:
            return f"Error downloading data for {self.rankingCategory}: {e}"


async def main(rankingCategory):
    from config import config
    async with aiohttp.ClientSession() as session:
        screener = StockAnalysis_IPO_Screener(rankingCategory, config, session)
        data = await screener.download()
        return data

if __name__ == "__main__":
    print(asyncio.run(main('industry')))

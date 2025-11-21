import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的股息。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import json
import asyncio

class StockAnalysis_Specific_Company_Dividend(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Dividend')
        self.source = 'stockanalysis.com'
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
        try:
            url = "https://stockanalysis.com/api/symbol/s/" + self.ticker + "/dividend"
            text = await self.request_get(url=url, headers=self.headers)
            data_dict = json.loads(text)["data"]
            del data_dict['chartOptions']
            del data_dict['news']
            del data_dict['meta']
            await self.db_connection.save_data(self.ticker, self.source, data_dict)
        except Exception as e:
            return f"Error: {e}"
        return data_dict

async def main():
    c = StockAnalysis_Specific_Company_Dividend('BABA')
    result = await c.download()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定年份的 IPOs。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
import json
import asyncio

class StockAnalysis_Specific_Year_IPOs(Usable_IP):
    def __init__(self, year, args={}):
        super().__init__(args)
        self.year = year
        self.rankingCategory = ','.join(['sharesOffered', 'ds', 'marketCap', 'revenue', 'industry', 'country',
                                         'employees', 'netIncome', 'fcf', 'ipoPriceLow', 'ipoPriceHigh', 'sector',
                                         'founded', 'grossProfit', 'operatingIncome', 'eps', 'ebit', 'ebitda',
                                         'grossMargin', 'operatingMargin', 'profitMargin', 'fcfMargin', 'ebitdaMargin',
                                         'ebitMargin', 'cash', 'assets', 'liabilities', 'debt', 'equity', 'operatingCF',
                                         'investingCF', 'financingCF', 'netCF', 'capex', 'fcfPerShare', 'sharesOut',
                                         'isSpac', 'exchange'
                                         ])
        self.db_connection = AsyncMongoConnection('IPO_Date')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
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
        front_url = "https://stockanalysis.com/api/screener/s/f?m=ipoDate&s=desc&c=ipoDate,s,n,ipoPrice,"
        last_url = "&f=ipoDate-year-" + self.year + "&i=histip"
        try:
            url = front_url + self.rankingCategory + last_url
        except:
            url = front_url + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]["data"]
        await self.db_connection.save_data(
            self.year, self.source, data_dict)
        return data_dict

async def main(year):
    from config import config
    c = StockAnalysis_Specific_Year_IPOs(year, config)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('2023')))
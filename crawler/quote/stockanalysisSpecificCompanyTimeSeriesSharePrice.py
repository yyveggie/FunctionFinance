import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的历史股价和当前股价。
'''
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import json
import asyncio

class StockAnalysis_Specific_Company_Time_Series_Share_Price(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Time_Series_Share_Price')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"1ov6wil"',
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
        # 1 day
        # text_1d = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/1D/l', headers=self.headers)
        # day_1d = json.loads(text_1d)["data"]
        # # 5 days
        # text_5d = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/5D/l', headers=self.headers)
        # day_5d = json.loads(text_5d)["data"]
        # # 1 Month
        # text_1m = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/1M/l', headers=self.headers)
        # month_1m = json.loads(text_1m)["data"]
        # # Year to Date
        # text_ytd = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/YTD/l', headers=self.headers)
        # ytd = json.loads(text_ytd)["data"]
        # # 1 Year
        text_1y = await self.request_get(
            url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/1Y/l', headers=self.headers)
        year_1y = json.loads(text_1y)["data"]
        # 5 Years
        # text_5y = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/5Y/l/week', headers=self.headers)
        # year_5y = json.loads(text_5y)["data"]
        # # Max
        # text_max = await self.request_get(
        #     url='https://stockanalysis.com/api/charts/s/' + self.ticker + '/MAX/l/week', headers=self.headers)
        # max = json.loads(text_max)["data"]
        data = {
            # "1 day": day_1d,
            # "5 days": day_5d,
            # "1 Month": month_1m,
            # "Year to Date": ytd,
            "1 Year": year_1y,
            # "5 Years": year_5y,
            # "Max": max
        }
        data_dict = dict_to_split_dict(data)
        await self.db_connection.save_data(self.ticker, self.source, data_dict)
        return data_dict


async def main(ticker):
    c = StockAnalysis_Specific_Company_Time_Series_Share_Price(ticker)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('AAPL')))
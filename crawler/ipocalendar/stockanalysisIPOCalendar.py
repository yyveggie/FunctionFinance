import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载 IPO 日历: 包括本周 IPO, 下周 IPO, 下周之后的 IPO, 下载 IPO Filings 和 Withdrawn IPOs。
'''
import asyncio
import aiohttp
import json
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd


class StockAnalysis_IPO_Calendar(Usable_IP):
    def __init__(self, args={}, session=None):
        super().__init__(args)
        self.session = session
        self.rankingCategory = ','.join(['sharesOffered', 'ds', 'marketCap', 'revenue', 'industry', 'country',
                                         'employees', 'netIncome', 'fcf', 'ipoPriceLow', 'ipoPriceHigh', 'sector',
                                         'founded', 'grossProfit', 'operatingIncome', 'eps', 'ebit', 'ebitda',
                                         'grossMargin', 'operatingMargin', 'profitMargin', 'fcfMargin', 'ebitdaMargin',
                                         'ebitMargin', 'cash', 'assets', 'liabilities', 'debt', 'equity', 'operatingCF',
                                         'investingCF', 'financingCF', 'netCF', 'capex', 'fcfPerShare', 'sharesOut',
                                         'isSpac', 'exchange'
                                         ])
        self.db_connection = AsyncMongoConnection('IPO_Calendar')
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

    async def download_upcoming_ipos(self):
        upcoming_ipos = {}
        upcoming_ipos['type'] = 'upcoming_ipos'
        for i in ["thisweek", "nextweek", "afternextweek"]:
            url = "https://stockanalysis.com/api/screener/i/f"
            params = {
                "m": "ipoDate",
                "s": "asc",
                "c": "ipoDate,s,n,exchange,ipoPriceRange," + self.rankingCategory,
                "f": "ipoDate-isdate-" + i,
                "i": "futip"
            }
            try:
                response_text = await self.request_get(session=self.session, url=url, headers=self.headers, params=params)
                text = {i: json.loads(response_text)["data"]["data"]}
            except:
                text = {i: None}
            upcoming_ipos[i] = text
        data_dict = pd.DataFrame(upcoming_ipos).to_dict(orient='records')
        await self.db_connection.save_data('upcoming_ipos', self.source, data_dict)
        return data_dict

    async def download_filings(self):
        filings = {'type': 'filings'}
        url = "https://stockanalysis.com/api/screener/i/f"
        params = {
            "m": "filingDate",
            "s": "desc",
            "c": "filingDate,s,n,ipoPriceRange," + self.rankingCategory,
            "f": "ipoDate-isnull,ipoStatus-isnot-withdrawn",
            "i": "futip"
        }
        try:
            response_text = await self.request_get(session=self.session, url=url, headers=self.headers, params=params)
            if response_text:
                res = json.loads(response_text)
                filings['text'] = res["data"]["data"]
        except Exception as e:
            print(f"Error downloading filings: {e}")
            filings['text'] = None
        data_dict = pd.DataFrame(filings['text']).to_dict(orient='records')
        await self.db_connection.save_data('filings', self.source, data_dict)
        return data_dict

    async def download_withdrawn(self):
        withdrawn = {'type': 'withdrawn'}
        url = "https://stockanalysis.com/api/screener/i/f"
        params = {
            "m": "withdrawnDate",
            "s": "desc",
            "c": "withdrawnDate,s,n,ipoPriceRange," + self.rankingCategory,
            "f": "ipoStatus-is-withdrawn",
            "i": "futip"
        }
        try:
            response_text = await self.request_get(session=self.session, url=url, headers=self.headers, params=params)
            withdrawn['text'] = json.loads(response_text)["data"]["data"]
        except Exception as e:
            print(f"Error downloading withdrawn IPOs: {e}")
            withdrawn['text'] = None
        data_dict = pd.DataFrame(withdrawn['text']).to_dict(orient='records')
        await self.db_connection.save_data('withdrawn', self.source, data_dict)
        return data_dict


async def main():
    from config import config
    async with aiohttp.ClientSession() as session:
        c = StockAnalysis_IPO_Calendar(args=config, session=session)
        data = await c.download_upcoming_ipos()
        return data

if __name__ == "__main__":
    print(asyncio.run(main()))

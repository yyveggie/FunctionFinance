import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定频率内的最佳市场表现，如3年内市场表现最强劲的股票（Top Gainers）
'''
from crawler.utils import turn_to_one_dict
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime
import pandas as pd
import json
import asyncio

class StockAnalysis_Market_Mover(Usable_IP):
    def __init__(self, types, timeframe=None, rankingCategory=None, args={}):
        super().__init__(args)
        if rankingCategory is not None:
            self.rankingCategories = ','.join(rankingCategory)
        else:
            self.rankingCategories = ''
        self.timeframe = timeframe
        self.types = types
        self.db_connection = AsyncMongoConnection('Market_Mover')
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

    async def download_gainers(self):
        if self.timeframe == "today":
            timeframe = "change"
        elif self.timeframe == "week":
            timeframe = "ch1w"
        elif self.timeframe == "month":
            timeframe = "ch1m"
        elif self.timeframe == "ytd":
            timeframe = "chYTD"
        elif self.timeframe == "year":
            timeframe = "ch1y"
        elif self.timeframe == "3 years":
            timeframe = "ch3y"
        elif self.timeframe == "5 years":
            timeframe = "ch5y"
        elif self.timeframe == 'now':
            return pd.DataFrame()
        else:
            return pd.DataFrame()
        front_url = "https://stockanalysis.com/api/screener/s/f?m="
        mid_url = "&s=desc&c=no,s,n,ch1m,price,volume,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,volume-over-10000,marketCap-over-10000000,ch1m-over-0&p=1&i=stocks"
        url = front_url + timeframe + mid_url + self.rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        await self.db_connection.save_data('gainers_' + datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S') + '_' + self.timeframe, self.source, data)
        return pd.DataFrame(data)

    async def download_losers(self):
        if self.timeframe == "today":
            timeframe = "change"
        elif self.timeframe == "week":
            timeframe = "ch1w"
        elif self.timeframe == "month":
            timeframe = "ch1m"
        elif self.timeframe == "ytd":
            timeframe = "chYTD"
        elif self.timeframe == "year":
            timeframe = "ch1y"
        elif self.timeframe == "3 years":
            timeframe = "ch3y"
        elif self.timeframe == "5 years":
            timeframe = "ch5y"
        elif self.timeframe == 'now':
            return pd.DataFrame()
        else:
            return pd.DataFrame()
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m="
        mid_url = "&s=asc&c=no,s,n,ch1w,price,volume,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,volume-over-10000,marketCap-over-10000000,ch1w-under-0&p=1&i=stocks"
        url = front_url + timeframe + mid_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        await self.db_connection.save_data('losers_' + datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S') + '_' + self.timeframe, self.source, data)
        return pd.DataFrame(data)

    async def download_active_today(self):
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m=volume&s=desc&c=no,s,n,volume,price,change,marketCap,industry,"
        last_url = f"&cn=&f=price-over-1,volume-over-0,marketCap-over-1000000&p=1&i=stocks"
        url = front_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        return pd.DataFrame(data)

    # "Premarket Gainers" 指的是在正式交易时段开始之前的预市场交易中表现最好的股票。预市场交易通常发生在正规交易时段开始之前的几个小时内，这时投资者可以根据最新的新闻、财报发布或其他重大事件进行交易。
    async def download_premarket_gainers(self):
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m=premarketChangePercent&s=desc&c=no,s,n,premarketChangePercent,premarketPrice,close,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,premarketChangePercent-over-0,volume-over-1000,marketCap-over-1000000&p=1&i=stocks"
        url = front_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        return pd.DataFrame(data)

    # "Premarket Losers" 指的是在正式交易时段开始之前的预市场交易中表现最差的股票。预市场交易通常发生在正规交易时段开始之前的几个小时内，这时投资者可以根据最新的新闻、财报发布或其他重大事件进行交易。
    async def download_premarket_losers(self):
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m=premarketChangePercent&s=desc&c=no,s,n,premarketChangePercent,premarketPrice,close,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,premarketChangePercent-over-0,volume-over-1000,marketCap-over-1000000&p=1&i=stocks"
        url = front_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        return pd.DataFrame(data)

    # "After Hours Gainers" 指的是在正常交易时段结束后进行的盘后交易中表现最好的股票。盘后交易通常发生在正规交易时段结束后的几个小时内，投资者可以在这个时间内进行交易，反应在交易日结束后公布的公司新闻、财报或其他重大事件。
    async def download_after_hours_gainers(self):
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m=postmarketChangePercent&s=desc&c=no,s,n,postmarketChangePercent,postmarketPrice,close,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,postmarketChangePercent-over-0,volume-over-10000,marketCap-over-1000000&p=1&i=stocks"
        url = front_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        return pd.DataFrame(data)

    # "After Hours Gainers" 指的是在正常交易时段结束后进行的盘后交易中表现最好的股票。盘后交易通常发生在正规交易时段结束后的几个小时内，投资者可以在这个时间内进行交易，反应在交易日结束后公布的公司新闻、财报或其他重大事件。
    async def download_after_hours_losers(self):
        rankingCategories = ','.join(self.rankingCategories)
        front_url = "https://stockanalysis.com/api/screener/s/f?m=postmarketChangePercent&s=asc&c=no,s,n,postmarketChangePercent,postmarketPrice,close,marketCap,"
        last_url = f"&cn=&f=price-over-1,close-over-1,postmarketChangePercent-under-0,volume-over-10000,marketCap-over-1000000&p=1&i=stocks"
        url = front_url + rankingCategories + last_url
        response = await self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)["data"]
        del data_dict['resultsCount']
        data = turn_to_one_dict(data_dict["data"])
        return pd.DataFrame(data)

    async def download(self):
        alldata = {}
        for type in self.types:
            if type == 'gainers':
                data = await self.download_gainers()
                if not data.empty:
                    alldata['gainers'] = data.head(10).to_dict(orient='records')
            if type == 'losers':
                data = await self.download_losers()
                if not data.empty:
                    alldata['gainers'] = data.head(10).to_dict(orient='records')
            if type == 'most-active' or type == 'active today':
                data = await self.download_active_today()
                alldata['most-active'] = data.head(10).to_dict(orient='records')
            if type == 'premarket gainers':
                data = await self.download_premarket_gainers()
                alldata['premarket gainers'] = data.head(10).to_dict(orient='records')
            if type == 'premarket losers':
                data = await self.download_premarket_losers()
                alldata['premarket losers'] = data.head(10).to_dict(orient='records')
            if type == 'after hours gainers':
                data = await self.download_after_hours_gainers()
                alldata['after hours gainers'] = data.head(10).to_dict(orient='records')
            if type == 'after hours losers':
                data = await self.download_after_hours_losers()
                alldata['after hours losers'] = data.head(10).to_dict(orient='records')
            else:
                pass
        
        # 保存全部数据到数据库
        for category, data in alldata.items():
            await self.db_connection.save_data(f'{category}_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_{self.timeframe}', self.source, data)
        
        return alldata


async def main(types, timeframe=None):
    # ["gainers", "losers", "active today", "premarket gainers", "premarket losers", "after hours gainers", "after hours losers",
    #          "indexes", "most-active", "climate-leaders", "cryptocurrencies", "currencies", "most-followed"]
    c = StockAnalysis_Market_Mover(
        types=types, timeframe=timeframe, rankingCategory='')
    return await c.download()

if __name__ == "__main__":
    types = ["gainers"]
    timeframe = 'today'
    print(asyncio.run(main(types, timeframe)))
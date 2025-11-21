import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定板块(sectors)或指定行业(industries)的所有股票。
    默认按照市值降序排序。
'''
from crawler.utils import turn_to_one_dict
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
import json


class StockAnalysis_Specific_Sector(Usable_IP):
    def __init__(self, sector, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.sector = sector
        self.db_connection = MongoConnection('Sector')
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

    def download_sector(self):
        try:
            url = "https://stockanalysis.com/api/screener/s/f?m=marketCap&s=desc&c=no,s,n,marketCap,change,volume,revenue,price,peRatio,revenueGrowth,netIncome&f=sector-is-" + self.sector + "&dd=true&i=stocks"
            text = self.request_get_sync(url=url, headers=self.headers)
            sector = json.loads(text)["data"]
            del sector['resultsCount']
            data = turn_to_one_dict(sector["data"])
            self.db_connection.save_data(self.sector, self.source, data)
            return pd.DataFrame(data)
        except:
            return None


class StockAnalysis_Specific_Industry(Usable_IP):
    def __init__(self, industry, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.industry = industry
        self.db_connection = MongoConnection('Industry')
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

    def download_industry(self):
        try:
            url = "https://stockanalysis.com/api/screener/s/f?m=marketCap&s=desc&c=no,s,n,marketCap,change,volume,revenue,price,peRatio,revenueGrowth,netIncome&f=industry-is-" + \
                self.industry + "&dd=true&i=stocks"
            text = self.request_get_sync(url=url, headers=self.headers)
            industry = json.loads(text)["data"]
            del industry['resultsCount']
            data = turn_to_one_dict(industry["data"])
            self.db_connection.save_data(self.industry, self.source, data)
            return pd.DataFrame(data)
        except:
            return None


if __name__ == "__main__":
    c = StockAnalysis_Specific_Industry(industry='Coking Coal')
    print(c.download_industry())

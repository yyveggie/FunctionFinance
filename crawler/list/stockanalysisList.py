import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载各种列表。
'''
import time
import re
import math
import json
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd


class StockAnalysis_List(Usable_IP):
    def __init__(self, country, args={}):
        super().__init__(args)
        self.list_name = args['list_name']
        self.list = args["stock_list"]
        self.country = country
        self.rankingCategories = ','.join(args["ranking_category"])
        self.db_connection = AsyncMongoConnection('List')
        self.source = "stockanalysis.com"
        self.rounds = 5
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

    async def download_lists(self, delay=1):
        alldata = []
        intro = self.list["text"]
        front_url = self.list["front url"]
        last_url = self.list["last url"]
        url = front_url + self.rankingCategories + last_url
        text = await self.request_get(url=url, headers=self.headers)
        response = json.loads(text)
        page_num = int(response["data"]["resultsCount"])
        total_pages = math.ceil(page_num / 500)
        page_data = response["data"]["data"]
        alldata.append(pd.DataFrame(page_data))
        print("total pages:", total_pages)
        if total_pages > 1:
            for i in range(1, total_pages):
                print(f"crawling page {i+1}...")
                page = i + 1
                updated_last_url = re.sub(r"p=\d+", f"p={page}", last_url)
                url = front_url + self.rankingCategories + updated_last_url
                text = await self.request_get(url=url, headers=self.headers)
                response = json.loads(text)
                page_data = response["data"]["data"]
                alldata.append(pd.DataFrame(page_data))
                time.sleep(delay)
        final_dataframe = pd.concat(alldata, ignore_index=True)
        dict_data = final_dataframe.to_dict(orient='split')
        await self.db_connection.save_data(self.list_name, self.source, dict_data)
        return {"introduce": intro, "data": dict_data}

    async def download_lists_by_country(self):
        front_url = "https://stockanalysis.com/api/screener/s/f?m=marketCap&s=desc&c=no,s,n,price,marketCap"
        mid_url = "&f=country-is-"
        last_url = "&dd=true&i=stocks"
        if self.country == 'us' or self.country == 'US':
            self.country = 'united states'
        if ' ' in self.country:
            country = self.country.replace(' ', "%2520")
        elif self.country == "china" or self.country == "China" or self.country == "CHINA":
            country = "China!Hong%2520Kong"
        else:
            country = self.country
        url = front_url + mid_url + country + last_url
        text = await self.request_get(url=url, headers=self.headers)
        data = json.loads(text)["data"]
        dataframe = pd.DataFrame(data)
        await self.db_connection.save_data(country.replace('%2520', ' ').replace(
            '!', ', '), self.source, dataframe.to_dict(orient='split'))
        return dataframe

async def main(country):
    from config import config
    c = StockAnalysis_List(country=country, args=config)
    return await c.download_lists()

if __name__ == "__main__":
    print(asyncio.run(main('us')))
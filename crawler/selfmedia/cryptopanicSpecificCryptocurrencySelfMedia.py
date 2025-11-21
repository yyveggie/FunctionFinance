import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 cryptopanic 的 API 下载加密货币相关的最新自媒体的标题: https://cryptopanic.com/developers/api/
免费的 API 可以无限制使用
注意:
1. 免费的 API 一次最多请求200条媒体, 每次返回20条, 因此一共有10页
2. 这是 "kind": "media" 的爬取, 要获取关于 news 的数据, 见 news_cryptopanic_streaming.py
'''
import os
import time
import json
from urllib.parse import urljoin
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from tqdm import tqdm
import pandas as pd
from crawler.utils import check_url_sync, save_urls_sync

class Cryptopanic_Specific_Cryptocurrency_Self_Media(Usable_IP):
    def __init__(self, cryptocurrency, args={}):
        super().__init__(args)
        self.token = os.environ.get('Cryptopanic_TOKEN')
        self.cryptocurrency = cryptocurrency
        self.db_connection = MongoConnection('SelfMedia')
        self.source = "cryptopanic.com"
        self.rounds = 1

    def download(self, delay=0.1):
        base_url = 'https://cryptopanic.com/api/v1/posts/?auth_token='
        self.dataframe = pd.DataFrame()
        data = {
            "domain": [],
            "title": [],
            "published_at": [],
            # "slug": [],
            "url": [],
            "currencies": [],
            "votes": [],
        }
        for i in tqdm(range(self.rounds), desc="Processing tasks"):
            params = {
                # You can use any of UI filters using filter=(rising|hot|bullish|bearish|important|saved|lol)
                "filter": "rising",
                # Filter by currencies using currencies=CURRENCY_CODE1,CURRENCY_CODE2 (max 50)
                "currencies": self.cryptocurrency,
                # Available regions: en (English), de (Deutsch), nl (Dutch), es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский), tr (Türkçe), ar (عربي), cn (中國人), jp (日本), ko (한국인)
                "regions": "en,cn",
                # Filter by kind using kind=news. Default: all. Available values: news or media
                "kind": "media",
                "page": i+1
            }
            headers = {
                'user-agent': UserAgent().random,
            }
            response = self.request_get_sync(url=base_url+self.token, headers=headers, params=params)
            res = json.loads(response)
            results = res["results"]

            # 检查和筛选URL
            urls = [result["url"] for result in results]
            print('length of urls: {0}'.format(len(urls)))
            filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source='')
            print('length of filtered urls: {0}'.format(len(filtered_urls)))
            if len(filtered_urls) == 0:
                return '当前没有新的链接'
            
            for j in results:
                if j["url"] not in filtered_urls:
                    continue
                data["domain"].append(j["domain"])
                data["title"].append(j["title"])
                data["published_at"].append(j["published_at"])
                # data["slug"].append(j["slug"])
                data["url"].append(j["url"])
                data["currencies"].append(j["currencies"][0]["title"])
                data["votes"].append(j["votes"])
            time.sleep(delay)

        # 保存已处理的URL
        save_urls_sync(collection_name=self.source, url_list=data["url"], source='')
        
        self.dataframe = pd.concat([self.dataframe, pd.DataFrame(data)])
        dict_data = self.dataframe.to_dict(orient='records')
        self.db_connection.save_data(self.cryptocurrency, self.source, dict_data)
        return dict_data

def main(cryptocurrency):
    c = Cryptopanic_Specific_Cryptocurrency_Self_Media(cryptocurrency)
    return c.download()

if __name__ == "__main__":
    print(main('BTC'))
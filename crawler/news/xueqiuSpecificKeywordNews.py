import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从雪球网下载指定公司的帖子和内容。
    用中文关键词。
'''

import requests
import time
import json
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime
import pandas as pd

class Xueqiu_Specific_Keyword_News(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.dataframe = pd.DataFrame()
        self.db_connection = AsyncMongoConnection('News')
        self.source = 'xueqiu.com'
        self.rounds = 2
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'https://xueqiu.com/k?q=%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': UserAgent().random,
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    async def download(self, delay=0.5):
        """
        从雪球 API 下载指定关键词的帖子和内容。
        :return: 包含标题、内容和创建时间的字典列表。
        """
        url = "https://xueqiu.com/query/v1/search/status.json"
        await self._get_cookie()
        data_list = []
        for page in range(self.rounds):
            params = {
                'sortId': '1',
                'q': self.keyword,
                'count': '10',
                'page': page + 1,
            }
            # 使用 session 发送请求，确保 cookies 被传递
            res = self.session.get(url=url, headers=self.headers, params=params)
            print(f"Page {page + 1} - Status Code: {res.status_code}")
            print(f"Response Text: {res.text}")
            if res.status_code != 200:
                print(f"Request failed with status code {res.status_code}")
                break
            try:
                res_json = json.loads(res.text)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Response was: {res.text}")
                break
            posts = res_json.get("list", [])
            print(f"Page {page + 1} - Found {len(posts)} posts")
            for post in posts:
                data_list.append({
                    'title': post.get('title', ''),
                    'content': post.get('text', ''),
                    'create_time': datetime.fromtimestamp(post.get('created_at', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                })
            time.sleep(delay)
        # 转换为 DataFrame
        self.dataframe = pd.DataFrame(data_list)
        if not self.dataframe.empty:
            await self.db_connection.save_data(
                self.keyword, self.source, data_list, ordered=False)
        return data_list

    async def _get_cookie(self):
        first_url = "https://xueqiu.com/k"
        params = {
            'q': self.keyword
        }
        self.session = requests.session()
        res = self.session.get(headers=self.headers, url=first_url, params=params)
        if res.status_code != 200:
            print(f"Failed to get cookies, status code: {res.status_code}")
            return f"Connection error: {res.status_code}"
        print(f"Cookies: {self.session.cookies.get_dict()}")
        return self.session.cookies

async def main(keyword):
    c = Xueqiu_Specific_Keyword_News(keyword=keyword)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('阿里巴巴')))
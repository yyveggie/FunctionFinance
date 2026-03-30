import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从雪球网下载指定公司的帖子和内容。
    用中文关键词。
'''

import requests
import json
import asyncio
import re
from typing import Optional
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
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://xueqiu.com',
            'Referer': 'https://xueqiu.com/k?q=%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4',
            'User-Agent': UserAgent().random,
            'X-Requested-With': 'XMLHttpRequest',
        }

    def _extract_json_payload(self, text: str) -> Optional[dict]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r'<textarea[^>]*id="renderData"[^>]*>(.*?)</textarea>', text, re.S)
        if not match:
            return None

        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            return None

    def _is_waf_payload(self, payload: Optional[dict]) -> bool:
        if not isinstance(payload, dict):
            return False
        return any(str(key).startswith('_waf_') for key in payload.keys())

    async def download(self, delay=0.5):
        """
        从雪球 API 下载指定关键词的帖子和内容。
        :return: 包含标题、内容和创建时间的字典列表。
        """
        url = "https://xueqiu.com/query/v1/search/status.json"
        await self._get_cookie()
        data_list = []
        max_retries = 3
        for page in range(self.rounds):
            params = {
                'sortId': '1',
                'q': self.keyword,
                'count': '10',
                'page': page + 1,
            }
            res_json = None
            for attempt in range(1, max_retries + 1):
                try:
                    res = self.session.get(
                        url=url,
                        headers=self.headers,
                        params=params,
                        timeout=20
                    )
                except requests.RequestException as e:
                    print(f"Page {page + 1} - attempt {attempt} request error: {e}")
                    await asyncio.sleep(delay * attempt)
                    continue

                if res.status_code != 200:
                    print(f"Page {page + 1} - attempt {attempt} status code: {res.status_code}")
                    await asyncio.sleep(delay * attempt)
                    continue

                payload = self._extract_json_payload(res.text)
                if self._is_waf_payload(payload):
                    print(f"Page {page + 1} - attempt {attempt} blocked by WAF, refreshing cookies")
                    await self._get_cookie()
                    await asyncio.sleep(delay * attempt)
                    continue

                if payload is None:
                    print(f"Page {page + 1} - attempt {attempt} invalid JSON payload")
                    await asyncio.sleep(delay * attempt)
                    continue

                res_json = payload
                break

            if res_json is None:
                print(f"Page {page + 1} failed after {max_retries} retries")
                continue

            posts = res_json.get("list", [])
            print(f"Page {page + 1} - Found {len(posts)} posts")
            for post in posts:
                data_list.append({
                    'title': post.get('title', ''),
                    'content': post.get('text', ''),
                    'create_time': datetime.fromtimestamp(post.get('created_at', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                })
            await asyncio.sleep(delay)
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
        self.headers['User-Agent'] = UserAgent().random
        res = self.session.get(headers=self.headers, url=first_url, params=params, timeout=20)
        if res.status_code != 200:
            print(f"Failed to get cookies, status code: {res.status_code}")
            return f"Connection error: {res.status_code}"
        print(f"Cookies: {self.session.cookies.get_dict()}")
        return self.session.cookies

async def main(keyword):
    c = Xueqiu_Specific_Keyword_News(keyword=keyword)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('英伟达')))
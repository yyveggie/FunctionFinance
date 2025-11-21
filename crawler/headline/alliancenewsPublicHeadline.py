# -*- coding: utf-8 -*-
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
"""
Download daily financial news from Alliance News.
"""
from data_connection.mongodb import AsyncMongoConnection
from crawler.utils import check_url, save_urls
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import json
import time
import asyncio

class AllianceNews_Public_Headline(Usable_IP):
    def __init__(self):
        super().__init__()
        self.db_connection = AsyncMongoConnection('Headline')
        self.source = "alliancenews.com"
        self.rounds = 10

    def _get_headers(self):
        return {
            'User-Agent': UserAgent().random,
            'Referer': "https://www.ii.co.uk/news/source/alliance-news",
            'Ii-Consumer-Type': 'web.public',
            'authority': 'www.ii.co.uk',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }

    async def _download_page(self, url, headers, params):
        try:
            text = await self.request_get(url=url, headers=headers, params=params)
        except Exception as e:
            return None, f"Connection Error: {e}"
        content = json.loads(text)
        return content["results"], content.get("nextId")

    async def download(self, delay=0.5):
        '''
        :return
        [
            {
                'url':
                'title':
                'published_date':
            }
        ]
        '''
        url = "https://api-prod.ii.co.uk/api/1/content/articles"
        params = {
            'pageSize': 50,
            'source': 'ALLIANCE'
        }
        round_count = 0
        crawled_data = []
        while round_count < self.rounds:
            headers = self._get_headers()
            page_data, next_id = await self._download_page(url, headers, params)
            if page_data is None:
                break
            urlIds = [item['urlId'] for item in page_data if 'urlId' in item]
            print('length of urls: {0}'.format(len(urlIds)))
            filtered_urlIds = await check_url(collection_name=self.source, url_list=urlIds, source='')
            print('length of filtered urls: {0}'.format(len(filtered_urlIds)))
            filtered_urlIds = urlIds
            if len(filtered_urlIds) == 0:
                return '当前没有新的链接'
            for item in page_data:
                if 'urlId' in item and item['urlId'] in filtered_urlIds:
                    crawled_data.append({
                        'url': item['urlId'],
                        'title': item['title'],
                        'published_date': item['updated']
                    })
            if not next_id:
                break
            params["nextId"] = next_id
            time.sleep(delay)
            round_count += 1
        await self.db_connection.save_data("public", self.source, crawled_data)
        await save_urls(collection_name=self.source, url_list=[item['url'] for item in crawled_data], source='')
        return crawled_data

async def main():
    c = AllianceNews_Public_Headline()
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main()))
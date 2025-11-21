import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 seekingalpha 下载指定公司在指定时间段内（默认近2天）的新闻。
5.19: 不知道为什么很难获取到数据。
'''
import json
import asyncio
import aiohttp
from lxml import etree
from urllib.parse import urljoin
from crawler.utils import check_url, save_urls
from datetime import datetime, timedelta
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent

class SeekingAlpha_Specific_Company_News(Usable_IP):
    def __init__(self, ticker, args={}, session=None):
        super().__init__(args)
        self.session = session
        self.ticker = ticker
        self.day_num = 2  # 获取近2天内的新闻
        self.db_connection = AsyncMongoConnection('News')
        self.source = "seekingalpha.com"
        self.headers = {
            'authority': 'seekingalpha.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'if-none-match': 'W/"5806d5cfc3ff7565a5f9f40150026ba3"',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'User-Agent': UserAgent().random,
        }

    async def _gather_by_page(self):
        url = f"https://seekingalpha.com/api/v3/symbols/{self.ticker}/news"
        try:
            response_text = await self.request_get(session=self.session, url=url, headers=self.headers)
            data = json.loads(response_text)
            articles = data['data']

            processed_data = []
            current_date = datetime.now()
            days_ago = current_date - timedelta(days=self.day_num)
            
            # 检查和筛选URL
            urls = [article['links']['self'] for article in articles]
            print('length of urls: {0}'.format(len(urls)))
            filtered_urls = await check_url(collection_name=self.source, url_list=urls, source=self.ticker)
            print('length of filtered urls: {0}'.format(len(filtered_urls)))
            if len(filtered_urls) == 0:
                return '当前没有新的链接'

            tasks = []
            for article in articles:
                url = article['links']['self']
                if url not in filtered_urls:
                    continue
                publish_date = datetime.strptime(article['attributes']['publishOn'], '%Y-%m-%dT%H:%M:%S-%f:00')
                if publish_date > days_ago:
                    tasks.append(asyncio.create_task(self._fetch_and_process(url, article)))

            # 并发请求所有有效的文章URL
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Error processing URL: {result}")
                elif isinstance(result, dict):  # 只保存成功获取的数据
                    processed_data.append(result)

            # 保存已处理的URL
            await save_urls(collection_name=self.source, url_list=[data['url'] for data in processed_data], source=self.ticker)
            
            return processed_data  # 返回所有成功处理的数据
        except Exception as e:
            print(f"Error fetching or processing data: {e}")
            return []

    async def _fetch_and_process(self, url, article, max_retry=3):
        for i in range(max_retry):
            try:
                print(f"Fetching URL: {url}, attempt {i+1}/{max_retry}")
                content, status_code = await self._get_content(link=url)
                if status_code != 200:
                    raise Exception(f"Request failed with status code {status_code}")
                if not content:
                    raise Exception("Empty content")
                print(f"Successfully fetched URL: {url}")
                return {
                    'title': article['attributes']['title'],
                    'create_time': article['attributes']['publishOn'],
                    'url': url,
                    'content': content
                }
            except Exception as e:
                print(f"Error fetching URL: {url}, error: {e}")
                await asyncio.sleep(3)  # 重试前短暂等待
        print(f"Failed to fetch URL after {max_retry} retries: {url}")
        return Exception(f"Failed to fetch: {url}")  # 超过最大重试次数,返回异常对象

    async def _get_content(self, link):
        url_complete = urljoin('https://seekingalpha.com/', link)
        async with self.session.get(url_complete, headers=self.headers, timeout=10) as response:
            status_code = response.status
            text = await response.text()
            tree = etree.HTML(text, parser=None)
            content = tree.xpath("//*[@id='content']//div[@class='T2G6W']//text()")
            clean_content = ' '.join(content).replace(' ', ' ').replace('\n', '')
            return clean_content, status_code

    async def download(self):
        '''
        :return
        [
            {
                'title':
                'create_time':
                'url':
                'content':
            }
        ]
        '''
        result = await self._gather_by_page()
        await self.db_connection.save_data(self.ticker, self.source, result)
        return result

async def main(ticker):
    async with aiohttp.ClientSession() as session:
        crawler = SeekingAlpha_Specific_Company_News(
            ticker=ticker, session=session)
        data = await crawler.download()
        return data

if __name__ == "__main__":
    print(asyncio.run(main('AAPL')))
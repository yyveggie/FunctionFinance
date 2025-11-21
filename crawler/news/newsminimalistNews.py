import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

'''
从https://www.newsminimalist.com/下载过去24h的头条新闻, 包含内容。

解析有问题。
'''

from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree
from datetime import datetime, timedelta
from crawler.utils import check_url, save_urls

class NewsMinimalist_News(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.db_connection = AsyncMongoConnection('News')
        self.source = 'newsminimalist.com'
        self.headers = {
            "user-agent": UserAgent().random,
            "referer": "https://www.newsminimalist.com/",
            'authority': 'www.newsminimalist.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'if-none-match': 'W/"98ff0584b36d9a1514b7c2bc58a1eb67"',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }

    async def download(self, delay=0.5):
        data_list = []
        url = 'https://www.newsminimalist.com/'
        res = await self.request_get(url=url, headers=self.headers)
        html = etree.HTML(res, parser=None)

        titles = html.xpath('/html/body/div/main/div/div/section[3]/ol[2]/li/details/summary/div[1]/span[1]/text()')
        times = html.xpath('/html/body/div/main/div/div/section[3]/ol[2]/li/details/summary/span[2]/text()')
        contents = html.xpath('/html/body/div/main/div/div/section[3]/ol[2]/li/details/div[1]/p/text()/text()')
        urls = html.xpath('/html/body/div/main/div/div/section[3]/ol[2]/li/details/div[2]/div[1]/a[2]/@href')

        # 检查url,获取新的url
        print('length of urls: {0}'.format(len(urls)))
        filtered_urls = await check_url(collection_name=self.source, url_list=urls, source=self.source)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))

        if len(filtered_urls) > 0:
            for url in filtered_urls:
                # 找到当前url对应的索引
                index = urls.index(url)
                relative_time = times[index].strip().lstrip('<')
                now = datetime.now()
                try:
                    num = int(relative_time[:-1])
                except ValueError:
                    num = 0
                unit = relative_time[-1]
                if unit == 's':
                    delta = timedelta(seconds=num)
                elif unit == 'm':
                    delta = timedelta(minutes=num)
                elif unit == 'h':
                    delta = timedelta(hours=num)
                elif unit == 'd':
                    delta = timedelta(days=num)
                else:
                    raise ValueError(f'Unknown time unit: {unit}')
                absolute_time = now - delta
                data = {
                    "title": titles[index],
                    "create_time": absolute_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "content": contents[index],
                    "url": url
                }
                data_list.append(data)
            await self.db_connection.save_data('public', self.source, data_list)
            # 保存成功爬取的url
            await save_urls(collection_name=self.source, url_list=filtered_urls, source=self.source)
            return data_list
        else:
            print('当前没有新的链接')
            return []

async def main():
    c = NewsMinimalist_News()
    return await c.download()

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main()))
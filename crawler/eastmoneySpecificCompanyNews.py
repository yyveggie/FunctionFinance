from socket import timeout
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从东方财富股吧网站下载指定公司的帖子和内容，但实际上更像是新闻。
    经常被识别，不好获取。
'''
import asyncio
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from crawler.utils import check_url, save_urls
from lxml import etree

class Eastmoney_Specific_Company_News(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.db_connection = MongoConnection('News')
        self.source = "eastmoney.com"
        self.ticker = ticker
        self.data_list = []
        self.rounds = 1
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://guba.eastmoney.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "User-Agent": UserAgent().random
        }

    async def download(self):
        if self.rounds > 0:
            tasks = [asyncio.create_task(self._gather_pages(self.ticker, r)) for r in range(self.rounds)]
        else:
            r = 1
            error_count = 0
            tasks = []
            while 1:
                task = asyncio.create_task(self._gather_pages(self.ticker, r))
                tasks.append(task)
                r += 1
                if error_count > 5:
                    print("Connection Error")
                    break
        await asyncio.gather(*tasks)
        self.db_connection.save_data(self.ticker, self.source, self.data_list)
        return self.data_list

    async def _gather_pages(self, ticker, page):
        data = []
        url = f"https://guba.eastmoney.com/list,{ticker}_{page}.html"
        text = await self.request_get(url, headers=self.headers)
        if "error404_page" in text:
            url = f"https://guba.eastmoney.com/list,us{ticker}_{page}.html"
            text = await self.request_get(url, headers=self.headers)
        html = etree.HTML(text, parser=None)
        titles = html.xpath('//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr/td[3]/div/a/text()')
        links = html.xpath('//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr/td[3]/div/a/@href')
        last_updateds = html.xpath('//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr/td[5]/div/text()')
        print('length of urls: %d' % len(links))
        filtered_urls = await check_url(collection_name=self.source, url_list=links, source='')
        print('length of filtered_urls: %d' % len(filtered_urls))
        filtered_titles = []
        filtered_last_updateds = []
        for link, title, last_updated in zip(links, titles, last_updateds):
            if link in filtered_urls:
                filtered_titles.append(title)
                filtered_last_updateds.append(last_updated)

        for title, link, last_updated in zip(filtered_titles, filtered_urls, filtered_last_updateds):
            one_sample = dict()
            content = await self._gather_content(link)
            one_sample = {'title': title, 'link': link, 'content': content, 'last_updated': last_updated}
            self.data_list.append(one_sample)

        await save_urls(collection_name=self.source, url_list=filtered_urls, source='')

    async def _gather_content(self, link):
        url = 'https://guba.eastmoney.com' + link
        try:
            text = await asyncio.wait_for(self.request_get(url, headers=self.headers), timeout=3)
        except asyncio.TimeoutError:
            return ' '
        except Exception as e:
            return ' '
        
        try:
            html = etree.HTML(text, parser=None)
        except Exception as e:
            return ' '
        
        raw_content = html.xpath('//*[@id="zw_body"]//text()')
        try:
            content = "".join(str(x) for x in raw_content)
        except:
            content = raw_content
        return content

async def main():
    from config import config
    c = Eastmoney_Specific_Company_News(ticker='BABA', args=config)
    result = await c.download()
    return result

if __name__ == "__main__":
    print(asyncio.run(main()))
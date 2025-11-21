import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    把这个改为金融指标查询。
'''
import random
import asyncio
import re
from datetime import datetime, timedelta
from lxml import etree
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from playwright.async_api import async_playwright

class Google_Finance_Specific_Company_Headline(Usable_IP):
    def __init__(self, ticker_listing_exchange, args={}):
        super().__init__(args)
        self.ticker_listing_exchange = ticker_listing_exchange
        self.db_connection = AsyncMongoConnection('Headline')
        self.source = 'google.com'
        self.dataframe = pd.DataFrame()
        self.headers = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"116.0.5845.141"',
            'sec-ch-ua-full-version-list': '"Chromium";v="116.0.5845.141", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'service-worker-navigation-preload': 'true',
            'upgrade-insecure-requests': '1',
            "User-Agent": UserAgent().random
        }

    async def download_for_ticker(self, ticker):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(viewport={"width": 1920, "height": 1080}, no_viewport=True)
            page = await context.new_page()
            url = f"https://www.google.com/finance/quote/{ticker}"
            await asyncio.sleep(random.uniform(1, 3))  # 添加随机延迟
            await page.goto(url)
            
            # 如果出现cookie弹框,点击接受
            if await page.is_visible("text=全部接受"):
                await page.click("text=全部接受")
            
            await page.wait_for_selector('.yY3Lee')
            html_content = await page.content()
            await browser.close()
            return html_content

    async def parse_headlines(self, html_content):
        tree = etree.HTML(html_content, parser=None)
        data_list = []
        titles = tree.xpath('//*[@class="yY3Lee"]//div[@class="Yfwt5"]/text()')
        urls = tree.xpath('//*[@class="yY3Lee"]//div[@class="z4rs2b"]/a[1]/@href')
        published_dates = tree.xpath('//*[@class="yY3Lee"]//div[@class="Adak"]/text()')
        for i in range(len(titles)):
            one_sample = {}
            one_sample['title'] = titles[i]
            one_sample['url'] = urls[i]
            one_sample['published_date'] = self.convert_to_date(published_dates[i])
            data_list.append(one_sample)
        return data_list

    async def download(self):
        result = await self.download_for_ticker(self.ticker_listing_exchange)
        return result
    
    def convert_to_date(time_str):
        pattern = r"(\d+)\s*(?:days?|天)\s*(?:ago|前)"
        match = re.search(pattern, time_str, re.IGNORECASE)
        if match:
            days_ago = int(match.group(1))
            target_date = datetime.now() - timedelta(days=days_ago)
            return target_date.strftime("%Y-%m-%d")
        else:
            return None

async def main():
    crawler = Google_Finance_Specific_Company_Headline(ticker_listing_exchange='BABA:NYSE')
    return await crawler.download()

if __name__ == "__main__":
    print(asyncio.run(main()))
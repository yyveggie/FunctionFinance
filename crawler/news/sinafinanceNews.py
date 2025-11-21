import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从新浪财经下载指定时间间隔的头条新闻, 内容不完整。
'''
import time
import pytz
import json
import aiohttp
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from tqdm import tqdm
from lxml import etree
import numpy as np
import pandas as pd
from crawler.utils import check_url, save_urls


class SinaFinance_News(Usable_IP):
    def __init__(self, date, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.start_date = date
        self.end_date = date
        self.db_connection = AsyncMongoConnection('News')
        self.source = 'sinafinance.com'
        self.rounds = 1
        self.headers = {
            'authority': 'feed.mix.sina.com.cn',
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
            'user-agent': UserAgent().random
        }

    async def download(self):
        '''
        :return
        [
            {
                'title':
                'create_time':
                'url':
                'content':
                'keywords':
            }
        ]
        '''
        self.date_list = pd.date_range(self.start_date, self.end_date)
        for date in tqdm(self.date_list, desc="Downloading Titles..."):
            tmp = await self._gather_one_day(date)
            print("DataFrame columns:", tmp.columns)  # 添加这行
            print("DataFrame shape:", tmp.shape)      # 添加这行
            self.dataframe = pd.concat([self.dataframe, tmp])
        
        # 获取所有的url
        urls = self.dataframe['url'].tolist()
        print('length of urls: {0}'.format(len(urls)))
        
        # 检查url,获取新的url
        filtered_urls = await check_url(collection_name=self.source, url_list=urls, source=self.source)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        
        if len(filtered_urls) > 0:
            # 过滤出新的数据
            self.dataframe = self.dataframe[self.dataframe['url'].isin(filtered_urls)]
            await self.gather_content()
            self.dataframe.rename(columns={'ctime':'create_time'}, inplace=True)
            self.dataframe = self.dataframe[['content', 'create_time', 'keywords', 'title', 'url']]
            self.dataframe['create_time'] = self.dataframe['create_time'].dt.tz_convert(
                None).dt.strftime('%Y-%m-%d %H:%M:%S')
            data_list = self.dataframe.to_dict(orient='records')
            await self.db_connection.save_data('public', self.source, data_list)
            
            # 保存成功爬取的url
            await save_urls(collection_name=self.source, url_list=filtered_urls, source=self.source)
            return data_list
        else:
            print('当前没有新的链接')
            return []

    async def _gather_one_day(self, date, delay=0.1):
        end_timestamp = pd.to_datetime(f"{date} 16:00:00").timestamp()
        start_timestamp = end_timestamp - 60 * 60 * 24
        res = pd.DataFrame()
        for page in range(self.rounds):
            url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&etime={start_timestamp}&stime={end_timestamp}&ctime={end_timestamp}&date={date}&k=&num=&page={page}"
            response = await self.request_get(url=url, headers=self.headers)
            if response is not None:
                text = json.loads(response, strict=True)
                print("API Response:", text)  # 添加这行
                text = text["result"]
                text = text["data"]
                if len(text) == 0:
                    break
                for i in text:
                    for ii in i.keys():
                        i[ii] = [i[ii]]
                    tmp = pd.DataFrame(i)
                    res = pd.concat([res, tmp])
                time.sleep(delay)
        if res.shape[0] != 0:
            res.ctime = pd.to_datetime(
                res.ctime.astype('int'), unit="s", utc=True)
            res.mtime = pd.to_datetime(
                res.mtime.astype('int'), unit="s", utc=True)
            res.intime = pd.to_datetime(
                res.intime.astype('int'), unit="s", utc=True)
            tz = pytz.timezone("Asia/Shanghai")
            res.ctime = [t.astimezone(tz) for t in res.ctime]
            res.mtime = [t.astimezone(tz) for t in res.mtime]
            res.intime = [t.astimezone(tz) for t in res.intime]
        return res

    async def gather_content(self, delay=0.1):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, row in self.dataframe.iterrows():
                tasks.append(asyncio.ensure_future(self._gather_content_apply(row, session, delay)))
            await asyncio.gather(*tasks)

    async def _gather_content_apply(self, x, session, delay=0.1):
        url = x.url
        async with session.get(url, headers=self.headers) as response:
            if response.status == 200:
                html = await response.text()
                page = etree.HTML(html, parser=None)
                content = page.xpath("//*[@id='artibody']/p//text()")
                content = " ".join(content)
            else:
                content = np.nan
            
            self.dataframe.at[x.name, 'content'] = content
            await asyncio.sleep(delay)
    
async def main(date):
    c = SinaFinance_News(date=date)
    return await c.download()

if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    pprint(asyncio.run(main('2025-04-17')))
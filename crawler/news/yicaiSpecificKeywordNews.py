import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从第一财经下载指定公司的新闻。
用中文关键词。
'''
import re
import time
import json
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from urllib.parse import quote
from fake_useragent import UserAgent
from lxml import etree
import pandas as pd
from crawler.utils import check_url, save_urls
from datetime import datetime, timedelta

def convert_time(time_str):
    now = datetime.now()
    if '昨天' in time_str:
        date = now.date() - timedelta(days=1)
        time = re.search(r'\d{2}:\d{2}', time_str).group()
        return datetime.combine(date, datetime.strptime(time, '%H:%M').time()).strftime('%Y-%m-%d %H:%M:%S')
    elif '今天' in time_str:
        date = now.date()
        time = re.search(r'\d{2}:\d{2}', time_str).group()
        return datetime.combine(date, datetime.strptime(time, '%H:%M').time()).strftime('%Y-%m-%d %H:%M:%S')
    elif '前天' in time_str:
        date = now.date() - timedelta(days=2)
        time = re.search(r'\d{2}:\d{2}', time_str).group()
        return datetime.combine(date, datetime.strptime(time, '%H:%M').time()).strftime('%Y-%m-%d %H:%M:%S')
    elif '小时前' in time_str:
        hours = int(re.search(r'\d+', time_str).group())
        return (now - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    elif '分钟前' in time_str:
        minutes = int(re.search(r'\d+', time_str).group())
        return (now - timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return time_str

def process_data(data):
    for item in data:
        item['create_time'] = item.pop('creationDate')
        item['create_time'] = convert_time(item['create_time'])
    return data

class Yicai_Specific_Keyword_News(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.dataframe = pd.DataFrame()
        self.db_connection = AsyncMongoConnection('News')
        self.source = "yicai.com"
        self.rounds = 2

    async def download(self, delay=0.5):
        '''
        :return
        [
            {
                'title':
                'create_time':
                'content':
                'url':
            }
        ]
        '''
        url = "https://www.yicai.com/api/ajax/getSearchResult"
        headers = {
            'User-Agent': UserAgent().random,
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'Accept': '*/*',
            'Referer': f'https://www.yicai.com/search?keys={quote(self.keyword)}',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        for page in range(self.rounds):
            params = {
                'page': page,
                'pagesize': '10',
                'keys': self.keyword,
                'type': 0,
            }
            res = await self.request_get(url=url, headers=headers, params=params)
            res = json.loads(res)
            res = res['results']
            tmp = pd.DataFrame(res["docs"])
            self.dataframe = pd.concat([self.dataframe, tmp])
            time.sleep(delay)

        # 获取所有的url
        urls = self.dataframe['url'].tolist()
        print('length of urls: {0}'.format(len(urls)))
        filtered_urls = await check_url(collection_name=self.source, url_list=urls, source=self.keyword)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        
        if len(filtered_urls) > 0:
            # 过滤出新的数据
            self.dataframe = self.dataframe[self.dataframe['url'].isin(filtered_urls)]
            await self.enrich_dataframe_with_content()
            dataframe = self.dataframe.drop(['channelid', 'id', 'previewImage', 'tags', 'desc', 'source', 'topics', 'typeo', 'weight', 'author'], axis=1)
            dict_data = dataframe.to_dict(orient='records')
            dict_data = process_data(dict_data)  # 处理时间格式
            await self.db_connection.save_data(self.keyword, self.source, dict_data, ordered=False)
            
            # 保存成功爬取的url
            await save_urls(collection_name=self.source, url_list=filtered_urls, source=self.keyword)
            return dict_data
        else:
            print('当前没有新的链接')
            return []

    async def enrich_dataframe_with_content(self):
        tasks = []
        for url in self.dataframe['url']:
            tasks.append(asyncio.create_task(self._get_content(url)))
        contents = await asyncio.gather(*tasks)
        self.dataframe['content'] = contents

    async def _get_content(self, content_url):
        base_url = "https://www.yicai.com"
        headers = {
            'authority': 'www.yicai.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'if-none-match': 'W/"6a02-RkMV5OjJiaCjVXsj2qxVDDL8V6M"',
            'referer': f'https://www.yicai.com/search?keys={quote(self.keyword)}',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }
        try:
            res = await self.request_get(url=base_url+content_url, headers=headers)
            html = etree.HTML(res, parser=None)
            content = html.xpath('//*[@id="multi-text"]//text()')
            return ' '.join(content).replace('\r\n', ' ').strip()
        except:
            return ''

async def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_cn.json")

    # 读取 stocks_cn.json 文件
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            keywords = eval(data["keywords"])
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return []

    # 初始化结果记录
    results = []

    # 逐个关键词串行处理
    for keyword in keywords:
        print(f"开始处理关键词: {keyword}")
        c = Yicai_Specific_Keyword_News(keyword)

        try:
            data = await c.download()
            print(f"关键词: {keyword} 爬取成功，获取到 {len(data)} 条数据。")
            results.append((keyword, "成功", len(data)))
        except Exception as e:
            print(f"关键词: {keyword} 爬取失败，错误信息: {e}")
            results.append((keyword, "失败", 0))

    # 输出总结
    print("\n爬取总结：")
    for r in results:
        print(f"关键词: {r[0]}, 状态: {r[1]}, 数据条数: {r[2]}")

    return results

if __name__ == "__main__":
    asyncio.run(main())
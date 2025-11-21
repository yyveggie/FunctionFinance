import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 CNBC 下载与关键词有关的新闻。
    内容包括标题和内容, 不过有些内容可能短一点，因为要开通会员能看，大多数包含全部内容。
    关键词只能是英文。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from crawler.utils import check_url, save_urls
from fake_useragent import UserAgent
from lxml import etree
import pandas as pd
import json
import asyncio

class CNBC_Specific_Keyword_News(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.dataframe = pd.DataFrame()
        self.db_connection = AsyncMongoConnection('News')
        self.source = "cnbc.com"
        self.rounds = 10
        self.headers = {
            'User-Agent': UserAgent().random,
            'Referer': 'https://www.cnbc.com/',
            'authority': 'api.queryly.com',
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

    async def download(self, delay=0.5):
        '''
        :return
        [
            {
                'title':
                'url':
                'create_time':
                'summary':
                'content':
            },
        ]
        '''
        url = "https://api.queryly.com/cnbc/json.aspx"
        data = []
        for page in range(self.rounds):
            params = {
                'queryly_key': '31a35d40a9a64ab3',
                'query': self.keyword,
                'endindex': page*10,
                'batchsize': '10',
                'callback': '',
                'showfaceted': 'false',
                'timezoneoffset': '-480',
                'facetedfields': 'formats',
                'facetedkey': 'formats|',
                'facetedvalue': '!Press Release|',
                'sort': 'date',
                'additionalindexes': '4cd6f71fbf22424d,937d600b0d0d4e23,3bfbe40caee7443e,626fdfcd96444f28',
            }
            res = await self.request_get(
                url=url, headers=self.headers, params=params)
            res = json.loads(res)
            tmp = pd.DataFrame(res['results'])
            
            # 只保留需要的列
            tmp = tmp[['summary', 'url', 'datePublished', 'cn:title']]
            # 重命名列
            tmp = tmp.rename(columns={'cn:title': 'title', 'datePublished': 'create_time'})
            # 格式化日期
            tmp['create_time'] = pd.to_datetime(tmp['create_time'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
            # 获取所有的url
            urls = tmp['url'].tolist()
            print('length of urls: {0}'.format(len(urls)))
            # 检查url,获取新的url
            filtered_urls = await check_url(collection_name=self.source, url_list=urls, source=self.keyword)
            print('length of filtered urls: {0}'.format(len(filtered_urls)))
            filtered_urls = urls
            if len(filtered_urls) > 0:
                await self.applyAsync(self.get_content, filtered_urls, tmp)
                self.dataframe = pd.concat([self.dataframe, tmp])
                await save_urls(collection_name=self.source, url_list=filtered_urls, source=self.keyword)
                data = self.dataframe.to_dict(orient='records')
                await self.db_connection.save_data(
                    self.keyword, self.source, data, ordered=False)
            else:
                print('当前没有新的链接')
            
        return data

    async def get_content(self, url):
        response = await self.request_get(url=url, headers=self.headers)
        page = etree.HTML(response, parser=None)
        content = page.xpath(
            '//*[@id="MainContentContainer"]/div/div/div/div[3]/div[1]//text()')
        return "\n".join(content)

    async def applyAsync(self, func, urls, tmp):  # 新增tmp参数
        coroutines = []
        for url in urls:
            coroutine = func(url)
            coroutines.append(coroutine)
        
        contents = await asyncio.gather(*coroutines)
        
        # 将新的内容更新到tmp DataFrame中
        for url, content in zip(urls, contents):
            tmp.loc[tmp['url']==url, 'content'] = content

async def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_en.json")

    # 读取 stocks.json 文件
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            keywords = eval(data["keywords"])
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return

    # 初始化结果记录
    results = []

    # 逐个关键词串行处理（符合你的第 1 条要求）
    for keyword in keywords:
        print(f"开始处理关键词: {keyword}")
        c = CNBC_Specific_Keyword_News(keyword=keyword)

        try:
            # 串行等待每个关键词爬取完成（异步处理内部多个网页）
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
import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从东方财富股吧下载帖子。
'''
import time
import json
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from lxml import etree

class Eastmoney_Specific_Company_Post(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.db_connection = AsyncMongoConnection('Post')
        self.dataframe = pd.DataFrame()
        self.source = "eastmoney"
        self.ticker = ticker
        self.rounds = 2

    async def download(self, delay=0.5):
        headers = {
            'User-Agent': UserAgent().random
        }
        for page in range(self.rounds):
            try:
                url = f"https://guba.eastmoney.com/list,{self.ticker}_{page+1}.html"
                res = await self.request_get(url=url, headers=headers)
                res = etree.HTML(res)  # type: ignore
                res = res.xpath("//script")[3].xpath("text()")[0]
            except:
                url = f"https://guba.eastmoney.com/list,us{self.ticker}_{page+1}.html"
                res = await self.request_get(url=url, headers=headers)
                res = etree.HTML(res)  # type: ignore
                res = res.xpath("//script")[3].xpath("text()")[0]
            article_list, other_list = res.split('var article_list=')[
                1].strip(";").split(';    var other_list=')
            article_list = json.loads(article_list)
            tmp = pd.DataFrame(article_list['re'])
            self.dataframe = pd.concat([self.dataframe, tmp])
            time.sleep(delay)
        dataframe = self.dataframe[['post_title', 'post_publish_time']]
        data_list = dataframe.to_dict(orient='records')
        await self.db_connection.save_data(
            self.ticker, self.source, data_list)
        return data_list

async def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_en.json")

    # 读取 stocks_en.json 文件
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            tickers = eval(data["stocks"])
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return []

    # 初始化结果记录
    results = []

    # 逐个股票代码串行处理
    for ticker in tickers:
        print(f"开始处理股票: {ticker}")
        c = Eastmoney_Specific_Company_Post(ticker)

        try:
            data = await c.download()
            print(f"股票: {ticker} 爬取成功，获取到 {len(data)} 条数据。")
            results.append((ticker, "成功", len(data)))
        except Exception as e:
            print(f"股票: {ticker} 爬取失败，错误信息: {e}")
            results.append((ticker, "失败", 0))

    # 输出总结
    print("\n爬取总结：")
    for r in results:
        print(f"股票: {r[0]}, 状态: {r[1]}, 数据条数: {r[2]}")

    return results

if __name__ == "__main__":
    asyncio.run(main())
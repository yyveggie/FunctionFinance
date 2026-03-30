import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从东方财富股吧下载帖子。
'''
import json
import asyncio
import re
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd

class Eastmoney_Specific_Company_Post(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.db_connection = AsyncMongoConnection('Post')
        self.dataframe = pd.DataFrame()
        self.source = "eastmoney"
        self.ticker = ticker
        self.rounds = 2

    def _extract_article_list(self, html_text, url):
        match = re.search(r"var\s+article_list\s*=\s*(\{.*?\})\s*;\s*var\s+other_list=", html_text, re.S)
        if not match:
            raise ValueError(f"未提取到 article_list，可能是股票代码无效或页面结构变化: {url}")

        payload = json.loads(match.group(1))
        rows = payload.get('re')
        if not isinstance(rows, list):
            raise ValueError(f"article_list.re 结构异常: {url}")
        return rows

    async def download(self, delay=0.5):
        headers = {
            'User-Agent': UserAgent().random
        }
        for page in range(self.rounds):
            mainland_url = f"https://guba.eastmoney.com/list,{self.ticker}_{page+1}.html"
            us_url = f"https://guba.eastmoney.com/list,us{self.ticker}_{page+1}.html"

            last_error = None
            rows = None

            for url in (mainland_url, us_url):
                try:
                    html_text = await self.request_get(url=url, headers=headers)
                    rows = self._extract_article_list(html_text, url)
                    break
                except Exception as e:
                    last_error = e

            if rows is None:
                raise ValueError(f"ticker={self.ticker} page={page+1} 抓取失败: {last_error}")

            tmp = pd.DataFrame(rows)
            self.dataframe = pd.concat([self.dataframe, tmp])
            await asyncio.sleep(delay)
        dataframe = self.dataframe[['post_title', 'post_publish_time']]
        data_list = dataframe.to_dict(orient='records')
        await self.db_connection.save_data(
            self.ticker, self.source, data_list)
        return data_list

async def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_cn.json")

    # 读取股票/关键词配置
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            raw_tickers = data.get("stocks") or data.get("keywords") or data.get("tickers")
            if raw_tickers is None:
                print(f"文件中未找到可用字段，期望: stocks / keywords / tickers, 文件: {stocks_file_path}")
                return []

            if isinstance(raw_tickers, str):
                tickers = json.loads(raw_tickers)
            elif isinstance(raw_tickers, list):
                tickers = raw_tickers
            else:
                print(f"字段类型不支持: {type(raw_tickers).__name__}, 文件: {stocks_file_path}")
                return []

            if not tickers:
                print(f"股票列表为空: {stocks_file_path}")
                return []
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"配置解析失败: {stocks_file_path}, 错误: {e}")
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
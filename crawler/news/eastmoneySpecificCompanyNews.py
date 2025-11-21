# 个股新闻
# 接口: stock_news_em
# 目标地址: https://so.eastmoney.com/news/s
# 描述: 东方财富指定个股的新闻资讯数据
# 限量: 指定 symbol 当日最近 100 条新闻资讯数据

import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import akshare as ak
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from crawler.utils import check_url_sync, save_urls_sync
import json

class Eastmoney_Specific_Company_News(Usable_IP):
    def __init__(self, ticker, args=None):
        super().__init__(args)
        self.db_connection = MongoConnection('News')
        self.source = "eastmoney.com"
        self.ticker = ticker

    def download(self):
        '''
        :return
        [
            'url':
            'summary':
            'title':
            'source':
            'create_time':
        ]
        '''
        temp_df = ak.stock_news_em(symbol=self.ticker)
        temp_df.rename(
            columns={
                "发布时间": "create_time",
                "文章来源": "source",
                "新闻标题": "title",
                "新闻内容": "summary",
                "新闻链接": "url",
            },
            inplace=True,
        )
        
        urls = temp_df['url'].tolist()
        print('length of urls: {0}'.format(len(urls)))
        filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source=self.ticker)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        
        if len(filtered_urls) > 0:
            temp_df = temp_df[temp_df['url'].isin(filtered_urls)]
            data_list: list = temp_df.to_dict(orient='records')
            data_list = [{k: v for k, v in d.items() if k != '关键词'} for d in data_list]
            self.db_connection.save_data(self.ticker, self.source, data_list)
            save_urls_sync(collection_name=self.source, url_list=filtered_urls, source=self.ticker)
            
            return data_list
        else:
            print('当前没有新的链接')
            return []

def main():
    from config import config
    
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_cn.json")

    # 读取 stocks_en.json 文件
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            tickers = eval(data["keywords"])
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return []

    # 初始化结果记录
    results = []

    # 逐个股票代码串行处理
    for ticker in tickers:
        print(f"开始处理股票: {ticker}")
        c = Eastmoney_Specific_Company_News(ticker, config)

        try:
            data = c.download()
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
    main()
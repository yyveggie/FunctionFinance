import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 Stocktwits 下载指定公司的帖子。
'''
import json
from fake_useragent import UserAgent
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP

class Stocktwits_Specific_Company_Post(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Post')
        self.source = 'stocktwits.com'
        self.headers = {
            'User-Agent': UserAgent().random,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'if-none-match': 'W/"070e5349b0a5ffdffee5714764bec50b"',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }

    def download(self):
        data_list = []
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{self.ticker}.json"
        response = self.request_get_sync(url, headers=self.headers)
        text = json.loads(response)
        posts = text['messages']
        for i in posts:
            data_dict = {}
            data_dict['post'] = i["body"]
            data_dict['created_at'] = i["created_at"]
            data_list.append(data_dict)
        self.db_connection.save_data(self.ticker, self.source, data_list)
        return data_list

def main():
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
        c = Stocktwits_Specific_Company_Post(ticker)

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
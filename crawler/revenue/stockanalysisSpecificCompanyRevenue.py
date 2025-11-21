import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的收入变化。
'''
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import json


class StockAnalysis_Specific_Company_Revenue(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Revenue')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"15z1wvg"',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    def download(self):
        url = "https://stockanalysis.com/api/symbol/s/" + self.ticker + "/revenue"
        text = self.request_get_sync(url=url, headers=self.headers)
        data = json.loads(text)["data"]
        revenue = {"info_box": data["info_box"],
                   "data": data["data"], "stats": data["stats"]}
        data_dict = dict_to_split_dict(revenue)
        self.db_connection.save_data(self.ticker, self.source, data_dict)
        return data_dict

def main(ticker):
    c = StockAnalysis_Specific_Company_Revenue(ticker)
    return c.download()

if __name__ == "__main__":
    print(main("BRK.B"))

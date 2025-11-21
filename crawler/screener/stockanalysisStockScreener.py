import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 根据所选特征来筛选股票，但只能通过一个特征来筛选。
    注意，这个筛选机制还不是很了解，有时间再检查一下。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import json


class StockAnalysis_Stock_Screener(Usable_IP):
    def __init__(self, ranking_category=None, args={}):
        super().__init__(args)
        # self.rankingCategory = args["ranking_category"][0]
        self.rankingCategory = ranking_category
        self.db_connection = MongoConnection('Stock_Screener')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"1ov6wil"',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
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
        url = "https://stockanalysis.com/api/screener/s/d/" + self.rankingCategory + ".json"
        response = self.request_get(url=url, headers=self.headers)
        data_dict = json.loads(response)['data']
        self.db_connection.save_data(
            self.rankingCategory, self.source, data_dict)
        return data_dict

if __name__ == "__main__":
    from config import config
    c = StockAnalysis_Stock_Screener(config)
    print(c.download())

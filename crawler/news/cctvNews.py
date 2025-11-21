import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 akshare 调用 CCTV 新闻联播文稿的接口。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from tqdm import tqdm
import akshare as ak
import pandas as pd

class CCTV_News(Usable_IP):
    def __init__(self, date, args={}):
        super().__init__(args)
        self.start_date = date
        self.end_date = date
        self.db_connection = MongoConnection('News')
        self.source = "cctv.com"

    def download(self):
        '''
        :return List[str]
        :params
            content
            title
            create_time
        '''
        self.date_list = pd.date_range(self.start_date, self.end_date)
        for date in tqdm(self.date_list):
            tmp = self.gather_one_day_news(date)
            dict_data_full = tmp.to_dict(orient='records')
            self.db_connection.save_data('public', self.source, dict_data_full)
        return dict_data_full

    def gather_one_day_news(self, date):
        date = self.transfer_standard_date_to_nonstandard(date)
        res = ak.news_cctv(date=date)
        return res

    def transfer_standard_date_to_nonstandard(self, date):
        return date.strftime("%Y-%m-%d")

def main(date):
    c = CCTV_News(date=date)
    return c.download()

if __name__ == "__main__":
    from crawler import datetime_utils
    today = datetime_utils.yyyymmdd()
    print(main(today))
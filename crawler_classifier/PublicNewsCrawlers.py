import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载公共新闻，不需要指定公司或者关键词。
'''
from crawler.news.sinafinanceNews import SinaFinance_News
from crawler.news.newsminimalistNews import NewsMinimalist_News
from crawler.news.mxnzpNews import Mxnzp_News
from crawler.news.cctvNews import CCTV_News
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PublicNewsCrawlerFunctions(object):
    def __init__(self, date) -> None:
        self.date = date
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            # threading.Thread(target=self.CCTV),
            threading.Thread(target=self.Mxnzp),
            # threading.Thread(target=self.NewsMinimalist),
            threading.Thread(target=self.SinaFinance)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def CCTV(self):
        cctv = CCTV_News(self.date)
        try:
            data = cctv.download()
            self.alldata["cctv"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in cctv_news: %s", e)
            self.alldata["cctv"] = "Error in collecting data"

    def Mxnzp(self):
        mxnzp = Mxnzp_News()
        try:
            data = mxnzp.download()
            self.alldata["mxnzp"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in mxnzp_news: %s", e)
            self.alldata["mxnzp"] = "Error in collecting data"

    def NewsMinimalist(self):
        newsminimalist = NewsMinimalist_News()
        try:
            data = newsminimalist.download()
            self.alldata["newsminimalist"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in newsminimalist_news: %s", e)
            self.alldata["newsminimalist"] = "Error in collecting data"

    def SinaFinance(self):
        sinafinance = SinaFinance_News(self.date)
        try:
            data = sinafinance.download()
            self.alldata["sinafinance"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in sinafinance_news: %s", e)
            self.alldata["sinafinance"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    c = PublicNewsCrawlerFunctions('2024-03-28')
    data = c.return_data()
    print(data)

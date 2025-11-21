import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个公司（股票）的帖子，帖子是不包含评论的。
'''
from crawler.post.stocktwitsSpecificCompanyPost import Stocktwits_Specific_Company_Post
from crawler.post.eastmoneySpecificCompanyPost import Eastmoney_Specific_Company_Post
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanyPostCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Eastmoney),
            threading.Thread(target=self.Stocktwits),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Eastmoney(self):
        eastmoney = Eastmoney_Specific_Company_Post(self.ticker)
        try:
            data = eastmoney.download()
            self.alldata["eastmoney"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in eastmoney_post: %s", e)
            self.alldata["eastmoney"] = "Error in collecting data"

    def Stocktwits(self):
        stocktwits = Stocktwits_Specific_Company_Post(self.ticker)
        try:
            data = stocktwits.download()
            self.alldata["stocktwits"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in stocktwits_post: %s", e)
            self.alldata["stocktwits"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    c = SpecificCompanyPostCrawlerFunctions('AAPL')
    print(c.return_data())

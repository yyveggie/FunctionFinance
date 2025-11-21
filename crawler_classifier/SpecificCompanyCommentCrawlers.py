import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个公司的帖子和评论。
'''
from crawler.post.eastmoneySpecificCompanyComment import Eastmoney_Specific_Company_Post
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanyCommentCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Eastmoney),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Eastmoney(self):
        eastmoney = Eastmoney_Specific_Company_Post(self.ticker)
        try:
            data = eastmoney.download()
            self.alldata['eastmoney'] = data.to_dict(orient='split')
        except Exception as e:
            logging.error('Error in eastmoney_comment: %s', e)

    def return_data(self):
        return self.alldata

if __name__ == '__main__':
    c = SpecificCompanyCommentCrawlerFunctions('AAPL')

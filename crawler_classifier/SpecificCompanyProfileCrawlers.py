import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    关于指定股票的公司的概述和雇员情况。
'''
from crawler.profile.stockanalysisSpecificCompanyProfile import StockAnalysis_Specific_Company_Profile
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ProfileCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.StockAnalysis),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def StockAnalysis(self):
        stockanalysis = StockAnalysis_Specific_Company_Profile(self.ticker)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = ProfileCrawlerFunctions('AAPL')
    print(c.return_data())

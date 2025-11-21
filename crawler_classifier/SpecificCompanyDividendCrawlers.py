import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定股票的股息。
'''
from crawler.dividend.stockanalysisSpecificCompanyDividend import StockAnalysis_Specific_Company_Dividend
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class DividendCrawlerFunctions(object):
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
        stockAnalysis = StockAnalysis_Specific_Company_Dividend(self.ticker)
        data = stockAnalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = DividendCrawlerFunctions('AAPL')
    alldata = c.return_data()
    print(alldata)

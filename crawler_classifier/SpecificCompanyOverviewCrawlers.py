import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    关于指定股票的表现概述, 包括最新的市值、收入、净利润什么的, 以及购买建议等。
'''
from crawler.overview.stockanalysisSpecificCompanyOverview import StockAnalysis_Specific_Company_Overview
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificCompanyOverviewCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Overview(self.ticker)
        data = stockanalysis.download()
        self.alldata["overview"] = data

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = SpecificCompanyOverviewCrawlerFunctions('BABA')
    print(c.return_data())

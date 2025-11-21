import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Income Statement.
'''
from crawler.incomestatement.stockanalysisSpecificCompanyIncomeStatement import StockAnalysis_Specific_Company_Income_Statement
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class IncomeStatementCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Income_Statement(
            self.ticker)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return json.dumps(self.alldata)


if __name__ == '__main__':
    c = IncomeStatementCrawlerFunctions('AAPL')
    data = c.return_data()
    print(data)

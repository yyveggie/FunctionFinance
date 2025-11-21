import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Download Cash Flow Statement.
'''
from crawler.cashflowstatement.stockanalysisSpecificCompanyCashFlowStatement import StockAnalysis_Specific_Company_Cash_Flow_Statement
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CashFlowStatementCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Cash_Flow_Statement(
            self.ticker)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return json.dumps(self.alldata)


if __name__ == '__main__':
    c = CashFlowStatementCrawlerFunctions('BABA')
    alldata = c.return_data()
    print(alldata)

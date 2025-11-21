import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定股票的收入变化。
'''
from crawler.revenue.stockanalysisSpecificCompanyRevenue import StockAnalysis_Specific_Company_Revenue
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RevenueCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Revenue(self.ticker)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return json.dumps(self.alldata)


if __name__ == '__main__':
    c = RevenueCrawlerFunctions('BABA')
    data = c.return_data()
    print(data)

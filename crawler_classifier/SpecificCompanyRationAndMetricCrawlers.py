import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定股票的年度各种金融比率和指标。
'''
from crawler.ratioandmetric.stockanalysisSpecificCompanyRationsandMetrics import StockAnalysis_Specific_Company_Ration_and_Metric
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RationAndMetricCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Ration_and_Metric(
            self.ticker)
        try:
            data = stockanalysis.download()
            self.alldata["stockanalysis"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_rations_and_metrics: %s", e)
            self.alldata["stockanalysis"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = RationAndMetricCrawlerFunctions('BABA')
    print(c.return_data())

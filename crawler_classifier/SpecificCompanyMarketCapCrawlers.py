import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定股票的市值变化。
'''
from crawler.marketcap.stockanalysisSpecificCompanyMarketCap import StockAnalysis_Specific_Company_MarketCap
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MarketCapCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.recent_marketcap),
            threading.Thread(target=self.all_marketcap),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def recent_marketcap(self):
        stockanalysis = StockAnalysis_Specific_Company_MarketCap(self.ticker)
        try:
            data = stockanalysis.download_recent_marketcap()
            self.alldata["recent_marketcap"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_recent_marketcap: %s", e)

    def all_marketcap(self):
        stockanalysis = StockAnalysis_Specific_Company_MarketCap(self.ticker)
        try:
            data = stockanalysis.download_all_marketcap()
            self.alldata["all_marketcap"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_all_marketcap: %s", e)

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = MarketCapCrawlerFunctions('BABA')
    data = c.return_data()
    print(data)

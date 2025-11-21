import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    根据所选特征来筛选股票。
'''
from crawler.screener.stockanalysisStockScreener import StockAnalysis_Stock_Screener
from config import config
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class StockScreenerCrawlerFunctions(object):
    def __init__(self) -> None:
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
        try:
            data = {"Prompt": "These are the filtered stocks according to the selected criteria downloaded from the stockanalysis.com."}
            stockanalysis = StockAnalysis_Stock_Screener(config)
            data["data"] = stockanalysis.download()
            self.alldata["stockanalysis_stock_screener"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_stock_screener: %s", e)
            self.alldata["stockanalysis_stock_screener"] = {
                "Prompt": "Error in collecting data", "data": "None"}

    def return_data(self):
        return self.alldata

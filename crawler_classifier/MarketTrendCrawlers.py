import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载整体市场信息。
'''
from crawler.marketmover.stockanalysisMarketMover import StockAnalysis_Market_Mover
from crawler.marketinformation.googlefinanceMarketInformation import GoogleFinance_Market_Dynamics
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MarketTrendCrawlerFunctions(object):
    def __init__(self, types, timeframe) -> None:
        self.alldata = {}
        self.types = types
        self.timeframe = timeframe
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.GoogleFinance),
            threading.Thread(target=self.StockAnalysis),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def GoogleFinance(self):
        googlefinance = GoogleFinance_Market_Dynamics(types=self.types, timeframe=self.timeframe)
        try:
            data = googlefinance.download()
            self.alldata["googlefinance"] = data
        except Exception as e:
            logging.error("Error in GoogleFinance: %s", e)

    def StockAnalysis(self):
        stockanalysis = StockAnalysis_Market_Mover(types=self.types, timeframe=self.timeframe, rankingCategory='')
        try:
            data = stockanalysis.download()
            self.alldata["stockanalysis"] = data
        except Exception as e:
            logging.error("Error in StockAnalysis: %s", e)

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    types = ["gainers", "losers", "active today", "premarket gainers", "premarket losers", "after hours gainers", "after hours losers",
             "indexes", "most-active", "climate-leaders", "cryptocurrencies", "currencies", "most-followed"]
    types = ["gainers", "losers", "indexes"]
    timeframe = 'now'
    c = MarketTrendCrawlerFunctions(types, timeframe)
    alldata = c.return_data()
    print(alldata)

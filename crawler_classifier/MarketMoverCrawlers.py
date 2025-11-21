import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载指定频率内的最佳市场表现，如3年内市场表现最强劲的股票（Top Gainers）。
'''
from crawler.marketmover.stockanalysisMarketMover import StockAnalysis_Market_Mover
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MarketMoverCrawlerFunctions(object):
    def __init__(self, type, timeframe) -> None:
        self.timeframe = timeframe
        self.type = type
        self.rankingCategory = ''
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
        stockanalysis = StockAnalysis_Market_Mover(
            types=self.type, timeframe=self.timeframe, rankingCategory=self.rankingCategory
        )
        try:
            data = stockanalysis.download()
            self.alldata = data
        except Exception as e:
            logging.error("Error in StockAnalysis gainers: %s", e)

    def return_data(self):
        return self.alldata


if __name__ == "__main__":
    crawler = MarketMoverCrawlerFunctions(['after hours gainers'], 'ytd')
    data = crawler.return_data()
    print(data)

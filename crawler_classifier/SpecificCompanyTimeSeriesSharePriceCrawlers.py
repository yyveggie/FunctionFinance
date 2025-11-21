import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    关于具体股票的历史报价数据和当前数据趋势。
'''
from crawler.quote.stockanalysisSpecificCompanyTimeSeriesSharePrice import StockAnalysis_Specific_Company_Time_Series_Share_Price
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class TimeSeriesSharePriceCrawlerFunctions(object):
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
        stockanalysis = StockAnalysis_Specific_Company_Time_Series_Share_Price(
            self.ticker)
        data = stockanalysis.download()
        self.alldata["stockanalysis"] = data

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    c = TimeSeriesSharePriceCrawlerFunctions('BABA')
    data = c.return_data()
    print(data)

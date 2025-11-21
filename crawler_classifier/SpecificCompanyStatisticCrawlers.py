import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    关于具体股票的统计数据, 比较笼统。
    可以分为基本面数据和市场数据。
'''
from crawler.statistic.stockanalysisSpecificCompanyStatistics import StockAnalysis_Specific_Company_Statistic
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class StatisticCrawlerFunctions(object):
    def __init__(self, tickers) -> None:
        self.tickers = tickers
        self.fundamental_data = {}
        self.market_data = {}
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
        fundamental_keys = [
            'valuation', 'financialPosition', 'financialEfficiency',
            'cashFlow', 'incomeStatement', 'balanceSheet', 'dividends',
            'taxes', 'margins', 'scores', 'shares'
        ]
        market_keys = [
            'stockPrice', 'shortSelling', 'analystForecasts', 'stockSplits'
        ]
        stockanalysis = StockAnalysis_Specific_Company_Statistic(self.tickers)
        data = stockanalysis.download()
        for key in market_keys:
            if key in data:
                self.market_data[key] = data[key]
        for key in fundamental_keys:
            if key in data:
                self.fundamental_data[key] = data[key]

    def return_data(self):
        return self.market_data, self.fundamental_data


if __name__ == '__main__':
    c = StatisticCrawlerFunctions('BABA')
    market_data, fundamental_data = c.return_data()
    # print(fundamental_data)
    print(market_data)

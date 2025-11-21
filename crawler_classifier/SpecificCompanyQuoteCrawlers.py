import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    关于指定股票的报价数据。
'''
from crawler.quote.stockanalysisSpecificCompanyQuote import StockAnalysis_Specific_Company_Quote
from crawler.quote.googlefinanceSpecificCompanyQuote import Google_Finance_Specific_Company_Quote
from crawler.quote.twseSpecificCompanyQuote import TWSE_Specific_Company_Quote
from crawler.quote.robinhoodSpecificCompanyQuote import Robinhood_Specific_Company_Quote
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class QuoteCrawlerFunctions(object):
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Robinhood),
            threading.Thread(target=self.TWSE),
            threading.Thread(target=self.GoogleFinance),
            threading.Thread(target=self.StockAnalysis),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Robinhood(self):
        robinhood = Robinhood_Specific_Company_Quote(self.ticker)
        try:
            data = robinhood.download()
            self.alldata["robinhood"] = data
        except Exception as e:
            logging.error("Error in robinhood_quote: %s", e)
            self.alldata["robinhood"] = "Error in collecting data"

    def TWSE(self):
        twse = TWSE_Specific_Company_Quote(self.ticker)
        try:
            data = twse.download()
            self.alldata["twse"] = data
        except Exception as e:
            logging.error("Error in twse_quote: %s", e)
            self.alldata["twse"] = "Error in collecting data"

    def GoogleFinance(self):
        googlefinance = Google_Finance_Specific_Company_Quote(self.ticker)
        try:
            data = googlefinance.download()
            self.alldata["googlefinance"] = data
        except Exception as e:
            logging.error("Error in googlefinance_quote: %s", e)
            self.alldata["googlefinance"] = "Error in collecting data"

    def StockAnalysis(self):
        stockanalysis = StockAnalysis_Specific_Company_Quote(self.ticker)
        try:
            data = stockanalysis.download()
            self.alldata["stockanalysis"] = data
        except Exception as e:
            logging.error("Error in stockanalysis_quote: %s", e)
            self.alldata["stockanalysis"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == "__main__":
    crawler = QuoteCrawlerFunctions('BABA')
    data = crawler.return_data()
    print(data)

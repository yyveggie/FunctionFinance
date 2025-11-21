import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
下载某个关键词的头条。
'''
from crawler.headline.pennystocksSpecificKeywordHeadline import PennyStocks_Specific_Keyword_Headline
from crawler.news.marketwatchSpecificKeywordNews import MarketWatch_Specific_Keyword_Headline
from crawler.news.investorplaceSpecificKeywordNews import InvestorPlace_Specific_Keyword_Headline
import threading
import logging
import json
from threading import Timer
import time

logging.basicConfig(filename='function_calling.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TIMEOUT = 20  # 设置超时时间为60秒

class TimeoutError(Exception):
    pass

class SpecificKeywordHeadlineCrawlerFunctions(object):
    def __init__(self, keyword) -> None:
        self.keyword = keyword
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.run_with_timeout, args=(self.InvestorPlace,)),
            # threading.Thread(target=self.run_with_timeout, args=(self.MarketWatch,)),
            threading.Thread(target=self.run_with_timeout, args=(self.PennyStocks,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def run_with_timeout(self, func):
        timer = Timer(TIMEOUT, self.handle_timeout, args=[func.__name__])
        timer.start()
        try:
            start_time = time.time()
            func()
            if time.time() - start_time > TIMEOUT:
                raise TimeoutError(f"Timeout for {func.__name__} crawler")
        finally:
            timer.cancel()

    def handle_timeout(self, func_name):
        logging.error(f"Timeout for {func_name} crawler")
        self.alldata[func_name.lower()] = "Timeout in collecting data"

    def InvestorPlace(self):
        investorplace = InvestorPlace_Specific_Keyword_Headline(self.keyword)
        try:
            data = investorplace.download()
            self.alldata["investorplace"] = data.to_json(orient='records', date_format='iso')
        except Exception as e:
            logging.error("Error in investorplace_headlines: %s", e)
            self.alldata["investorplace"] = "Error in collecting data"

    def MarketWatch(self):
        marketwatch = MarketWatch_Specific_Keyword_Headline(self.keyword)
        try:
            data = marketwatch.download()
            self.alldata["marketwatch"] = data.to_json(orient='records', date_format='iso')
        except Exception as e:
            logging.error("Error in marketwatch_headlines: %s", e)
            self.alldata["marketwatch"] = "Error in collecting data"

    def PennyStocks(self):
        pennystocks = PennyStocks_Specific_Keyword_Headline(self.keyword)
        try:
            data = pennystocks.download()
            self.alldata["pennystocks"] = data.to_json(orient='records', date_format='iso')
        except Exception as e:
            logging.error("Error in pennystocks_headlines: %s", e)
            self.alldata["pennystocks"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)

if __name__ == '__main__':
    c = SpecificKeywordHeadlineCrawlerFunctions('apple')
    print(c.return_data())
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_community.tools.polygon.ticker_news import PolygonTickerNews
from langchain_community.utilities.polygon import PolygonAPIWrapper
import os
import json
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


api_wrapper = PolygonAPIWrapper(polygon_api_key=os.getenv('POLYGON_API_KEY'))
ticker_news_tool = PolygonTickerNews(api_wrapper=api_wrapper)

class SpecificCompanyNewsCrawlerFunctions(object):
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
        ticker_news = ticker_news_tool.run(self.ticker)
        self.alldata["polygon"] = ticker_news

    def return_data(self):
        return json.dumps(self.alldata)


if __name__ == '__main__':
    c = SpecificCompanyNewsCrawlerFunctions('BABA')
    print(c.return_data())

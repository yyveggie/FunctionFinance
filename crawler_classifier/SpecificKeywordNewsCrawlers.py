import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.news.yicaiSpecificKeywordNews import Yicai_Specific_Keyword_News
from crawler.news.cnbcSpecificKeywordNews import CNBC_Specific_Keyword_News
from crawler.news.tipranksSpecificKeywordNews import TipRanks_Specific_Keyword_News
from crawler.news.talkmarketsSpecificKeywordNews import TalkMarkets_Specific_Keyword_News
import concurrent.futures
import json
import logging
from threading import Thread
import time

logging.basicConfig(filename='function_calling.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpecificKeywordNewsCrawlerFunctions(object):
    def __init__(self, keyword) -> None:
        self.alldata = {}
        self.keyword = keyword
        self.run_in_parallel()

    def run_in_parallel(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                # executor.submit(self.run_with_timeout, self.TalkMarkets),
                # executor.submit(self.run_with_timeout, self.TipRanks),
                executor.submit(self.run_with_timeout, self.CNBC),
                executor.submit(self.run_with_timeout, self.YiCai),
            ]
            for future in futures:
                try:
                    future.result(timeout=30)
                except concurrent.futures.TimeoutError:
                    logging.error("Crawler task timeout, skipping...")
                except Exception as e:
                    logging.error("Error in crawler task: %s", e)

    def run_with_timeout(self, func):
        thread = Thread(target=func)
        thread.start()
        start_time = time.time()
        while thread.is_alive():
            if time.time() - start_time > 30:
                logging.error(f"Timeout for {func.__name__} crawler")
                break
        else:
            return

    def TalkMarkets(self):
        talkmarkets = TalkMarkets_Specific_Keyword_News(self.keyword)
        data = talkmarkets.download()
        self.alldata["talkmarkets"] = data.to_json(orient='records', date_format='iso', force_ascii=False)

    def TipRanks(self):
        tipranks = TipRanks_Specific_Keyword_News(self.keyword)
        data = tipranks.download()
        self.alldata["tipranks"] = data.to_json(orient='records', date_format='iso', force_ascii=False)

    def CNBC(self):
        cnbc = CNBC_Specific_Keyword_News(self.keyword)
        data = cnbc.download()
        self.alldata["cnbc"] = data.to_json(orient='records', date_format='iso', force_ascii=False)

    def YiCai(self):
        yicai = Yicai_Specific_Keyword_News(self.keyword)
        data = yicai.download()
        self.alldata["yicai"] = data.to_json(orient='records', date_format='iso', force_ascii=False)

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)

if __name__ == '__main__':
    c = SpecificKeywordNewsCrawlerFunctions('AI')
    print(c.return_data())
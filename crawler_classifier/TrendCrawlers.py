import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    搜索趋势下载。
'''
from crawler.trend.googleSpecificKeywordTrend import Google_Specific_Keyword_Trends
import json
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class TrendCrawlerFunctions(object):
    def __init__(self, keyword) -> None:
        self.alldata = {}
        self.keyword = keyword
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Google),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Google(self):
        try:
            google = Google_Specific_Keyword_Trends(self.keyword)
            data = google.download()
            self.alldata["google"] = data
        except Exception as e:
            logging.error("Error in google_trend: %s", e)
            self.alldata["google"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    c = TrendCrawlerFunctions('chatgpt')
    print(c.return_data())

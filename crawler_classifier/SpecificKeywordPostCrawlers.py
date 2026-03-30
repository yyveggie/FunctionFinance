import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个关键词的帖子。
'''
from crawler.news.xueqiuSpecificKeywordNews import Xueqiu_Specific_Keyword_News
from crawler.post.weiboSpecificKeywordPost import Weibo_Specific_Keyword_Post
from crawler.post.xSpecificKeywordPost import X_Specific_Keyword_Post
import threading
import logging
import json
import asyncio
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificKeywordPostCrawlerFunctions(object):
    def __init__(self, keyword) -> None:
        self.alldata = {}
        self.keyword = keyword
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            # threading.Thread(target=self.X),
            threading.Thread(target=self.WeiBo),
            threading.Thread(target=self.XueQiu),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def _normalize_records(self, data):
        to_dict = getattr(data, "to_dict", None)
        if callable(to_dict):
            return to_dict(orient='records')
        return data

    def X(self):
        x = X_Specific_Keyword_Post(self.keyword)
        try:
            data = x.download()
            self.alldata["x"] = self._normalize_records(data)
        except Exception as e:
            logging.error("Error in x_post: %s", e)
            self.alldata["x"] = "Error in collecting data"

    def WeiBo(self):
        weibo = Weibo_Specific_Keyword_Post(self.keyword)
        try:
            data = weibo.download()
            self.alldata["weibo"] = self._normalize_records(data)
        except Exception as e:
            logging.error("Error in weibo_post: %s", e)
            self.alldata["weibo"] = "Error in collecting data"

    def XueQiu(self):
        xueqiu = Xueqiu_Specific_Keyword_News(self.keyword)
        try:
            data = asyncio.run(xueqiu.download())
            self.alldata["xueqiu"] = self._normalize_records(data)
        except Exception as e:
            logging.error("Error in xueqiu_post: %s", e)
            self.alldata["xueqiu"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == '__main__':
    c = SpecificKeywordPostCrawlerFunctions('AI')
    print(c.return_data())

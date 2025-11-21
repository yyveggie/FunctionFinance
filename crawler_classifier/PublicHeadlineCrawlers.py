import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    Public 头条是不能选择关于某个关键词的头条。
'''
from crawler.headline.alliancenewsPublicHeadline import AllianceNews_Public_Headline
import json
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PublicHeadlineCrawlerFunctions(object):
    def __init__(self) -> None:
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.AllianceNews),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def AllianceNews(self):
        alliancenews = AllianceNews_Public_Headline()
        try:
            data = alliancenews.download()
            self.alldata['alliancenews'] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in allianceNews_headlines: %s", e)

    def return_data(self):
        return json.dumps(self.alldata, ensure_ascii=False)


if __name__ == "__main__":
    crawler = PublicHeadlineCrawlerFunctions()
    data = crawler.return_data()
    print(data)

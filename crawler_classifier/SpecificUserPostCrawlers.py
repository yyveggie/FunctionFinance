import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个用户的帖子。
'''
from crawler.user.xSpecificUserPost import X_Specific_User_Post
import threading
import logging
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SpecificUserPostCrawlerFunctions(object):
    def __init__(self, config) -> None:
        self.alldata = {}
        self.config = config
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.X),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def X(self):
        x = X_Specific_User_Post(self.config)
        try:
            self.alldata["x"] = x.download()
        except Exception as e:
            logging.error("Error in x_post: %s", e)
            self.alldata["x"] = "Error in collecting data"

    def return_data(self):
        return self.alldata


if __name__ == '__main__':
    from config import config
    c = SpecificUserPostCrawlerFunctions(config)
    print(c.return_data())

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    下载某个关键词的帖子和评论。
'''
from crawler.comment.redditSpecificKeywordComment import Reddit_Specific_Keyword_Comment
import threading
import logging
import json
logging.basicConfig(filename='function_calling.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RedditCommentCrawler(object):
    def __init__(self, subreddit) -> None:
        self.subreddit = subreddit
        self.alldata = {}
        self.run_in_parallel()

    def run_in_parallel(self):
        threads = [
            threading.Thread(target=self.Reddit),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def Reddit(self):
        try:
            reddit = Reddit_Specific_Keyword_Comment(self.subreddit)
            data = reddit.download()
            self.alldata["reddit"] = data.to_dict(orient='records')
        except Exception as e:
            logging.error("Error in reddit_comment: %s", e)
            self.alldata["reddit"] = "Error in collecting data"

    def return_data(self):
        return json.dumps(self.alldata)


if __name__ == '__main__':
    c = RedditCommentCrawler('Stocks')
    print(c.return_data())

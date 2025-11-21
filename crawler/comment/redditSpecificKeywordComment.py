import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 reddit 官方接口调用 subreddits 中帖子的下载: https://www.reddit.com/dev/api/oauth
    用户的设定: https://www.reddit.com/prefs/apps/
    参考网站: https://infatica.io/blog/scraping-reddit-with-scraper-api/#legality
    注意: 
        1.reddit 不反对爬虫, 但是限制每分钟上限60次请求, 每次请求最多100个项目。
'''
import os
import praw
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from praw.models import MoreComments

class Reddit_Specific_Keyword_Comment(Usable_IP):
    def __init__(self, subreddit, args={}):
        super().__init__(args)
        # self.listing = args['listing'][0]     # 默认是"top"
        # The Reddit API’s rate limit is up to 60 requests per minute. It allows a request to up to 100 items at once.
        self.count = 5  # 获取post数量，注意：单条post的评论会很多
        self.time_filter = 'day'  # 默认是"day"
        self.subreddit = subreddit
        self.reddit_read_only = praw.Reddit(
            client_id=os.environ.get('Reddit_CLIENTID'),
            client_secret=os.environ.get('Reddit_CLIENTSECRET'),
            user_agent=os.environ.get('Reddit_USERAGENT'))
        self.db_connection = MongoConnection('Comment')
        self.source='reddit.com'

    def download(self):
        data_list = []
        subreddit = self.reddit_read_only.subreddit(self.subreddit)
        try:
            posts = subreddit.top(time_filter=self.time_filter, limit=self.count)
        except Exception as e:
            return f"Request error: {e}"
        for post in posts:
            post_dict = {
                "title": [],
                "post": [],
                "id": [],
                "score": [],
                "total comments": [],
                "url": [],
                "comments": []
            }
            post_dict["title"] = post.title
            post_dict["post"] = post.selftext
            post_dict["id"] = post.id
            post_dict["score"] = post.score
            post_dict["total comments"] = post.num_comments
            post_dict["url"] = post.url
            post_dict["comments"] = self.get_comments(post.url)
            data_list.append(post_dict)
        self.db_connection.save_data(collection_name=self.subreddit, source=self.source, data=data_list)
        return data_list

    def get_comments(self, url):
        # Creating a submission object
        submission = self.reddit_read_only.submission(url=url)
        post_comments = []
        for comment in submission.comments:
            if type(comment) == MoreComments:
                continue
            post_comments.append(comment.body)
        return post_comments

def main(subreddit):
    c = Reddit_Specific_Keyword_Comment(subreddit)
    return c.download()

if __name__ == "__main__":
    print(main('ChinaStocks'))

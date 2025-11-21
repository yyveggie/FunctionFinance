import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.SpecificUserPostCrawlers import SpecificUserPostCrawlerFunctions
from langchain.tools import tool
from config import config


@tool('Crawl professionals tweets')
def get_twitter_user_posts():
    '''
    Useful to crawl posts from well-known users in the financial domain on Twitter.

    The tool does not need input.
    '''
    return SpecificUserPostCrawlerFunctions(config).return_data()


def tools():
    return [get_twitter_user_posts]


# if __name__ == '__main__':
#     print(get_twitter_user_posts())


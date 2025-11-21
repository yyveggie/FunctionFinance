import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.TrendCrawlers import TrendCrawlerFunctions
from langchain.tools import tool


@tool('Crawl google search trend')
def get_google_search_trend(keyword: str):
    '''
    Useful to crawl Google search trends for a specific keyword over a period of 10 days.

    Parameter:
        - keyword (str): The keyword you are interested in.
    For example: 'ChatGPT'.
    '''
    return TrendCrawlerFunctions(keyword).return_data()


def tools():
    return [get_google_search_trend]


# if __name__ == '__main__':
#     print(get_google_search_trend('chatgpt'))

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler_classifier.SpecificCryptocurrencyHeadlineCrawlers import SpecificCryptocurrencyHeadlineCrawlerFunctions
from crawler_classifier.SpecificCryptocurrencySelfMediaCrawlers import SpecificCryptocurrencySelfMediaCrawlerFunctions
from langchain.tools import tool


@tool('Crawl cryptocurrency discussions on social media')
def get_cryptocurrency_discussions(cryptocurrency: str):
    '''
    Useful to crawl specific cryptocurrency discussions on social media.

    Parameter:
        - cryptocurrency (str): The english abbreviation of a certain cryptocurrency.
    For example: 'BTC'.
    '''
    sm = SpecificCryptocurrencySelfMediaCrawlerFunctions(cryptocurrency)
    return sm.return_data()


@tool('Crawl cryptocurrency headlines')
def get_cryptocurrency_headlines(cryptocurrency: str):
    '''
    Useful to crawl specific cryptocurrency headlines(Only title, No content) you are interested in.

    Parameter:
        - cryptocurrency (str): The english abbreviation of a certain cryptocurrency.
    For example: 'BTC'.
    '''
    ch = SpecificCryptocurrencyHeadlineCrawlerFunctions(cryptocurrency)
    return ch.return_data()


def tools():
    return [get_cryptocurrency_discussions, get_cryptocurrency_headlines]


# if __name__ == '__main__':
#     print(get_cryptocurrency_discussions('BTC'))

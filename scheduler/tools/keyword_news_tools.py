import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.news import tipranksSpecificKeywordNews
from langchain.tools import tool

@tool('Scrape_Keyword_News')
def get_keyword_news(keyword: str):
    '''
    Useful to crawl news with specific keyword you are interested in.

    Parameter:
        - keyword (str): The keyword for the news you want to search.
    For example: 'stock'
    '''
    tr_news = tipranksSpecificKeywordNews.main(keyword)[:5]
    results = [i['content'] for i in tr_news]
    return results

def tools():
    return [get_keyword_news]


# if __name__ == '__main__':
#     print(get_keyword_news('AI'))


import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.news import finnhubNews
from langchain.tools import tool

@tool('Scrape_public_news')
def get_public_news(input):
    '''
    Useful to crawl world public news.
    
    This tool INPUT MUST BE 'public'.
    '''
    fh_news = finnhubNews.main()
    return [i['summary'] for i in fh_news][:10]

def tools():
    return [get_public_news]

if __name__ == '__main__':
    print(get_public_news(''))

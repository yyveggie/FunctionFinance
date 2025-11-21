import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain.tools import tool
from crawler.news import (
    cnbcSpecificKeywordNews,
    investorplaceSpecificKeywordNews,
)
import asyncio

@tool('Scrape_Company_News')
def get_company_news(ticker: str):
    '''
    Scrape news related to a specific company you are interested in.
    
    Parameter:
        - ticker (str): The ticker symbol of the company's stock.
    For example: ticker = 'AAPL'
    '''
    try:
        cnbc_news = asyncio.run(cnbcSpecificKeywordNews.main(ticker))[:5]
    except:
        pass
    try:
        ip_news = investorplaceSpecificKeywordNews.main(ticker)[:5]
    except:
        pass
    results = []
    for x, y in zip(cnbc_news, ip_news):
        results.append(x['content'] if x['content'] else None)
        results.append(y['content'] if y['content'] else None)
    return results

def tools():
    return [get_company_news]


if __name__ == '__main__':
    print(get_company_news('BABA'))

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.post import (
    eastmoneySpecificCompanyPost,
    weiboSpecificKeywordPost
)
from langchain.tools import tool
import asyncio

@tool('Scrape_Company_Posts')
def get_company_posts(ticker: str, keyword: str):
    '''
    Scrape posts related to specific company you are interested in.

    Parameter:
        - ticker (str): The ticker symbol of the company's stock.
        - keyword (str): The keyword in chinese of the company's name.
    For example: 'BABA', '阿里巴巴'
    '''
    try:
        eastmoney_posts = asyncio.run(eastmoneySpecificCompanyPost.main(ticker))[:5]
    except:
        pass
    try:
        weibo_posts = weiboSpecificKeywordPost.Weibo_Specific_Keyword_Post(keyword).download()[:5]
    except:
        pass
    results = []
    for x, y in zip(eastmoney_posts, weibo_posts):
        results.append(x['content'] if x['content'] else None)
        results.append(y['content'] if y['content'] else None)
    return results

def tools():
    return [get_company_posts]


# if __name__ == '__main__':
#     print(get_company_posts('NTES', '网易'))

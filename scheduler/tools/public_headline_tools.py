import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.headline import alliancenewsPublicHeadline
from langchain.tools import tool
import asyncio

@tool('Get_Public_Headlines')
def get_public_headlines(nothing: str):
    ''' 
    Useful to scrape world public headlines.
    
    This tool INPUT MUST BE 'public'.
    '''
    alliancenews_headlines = asyncio.run(alliancenewsPublicHeadline.main())
    results = [i['title'] for i in alliancenews_headlines]
    return results

def tools():
    return [get_public_headlines]

if __name__ == '__main__':
    print(get_public_headlines('nothing'))

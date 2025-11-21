import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from googlesearch.googlesearch import GoogleSearch
from config_loader import SEARCH_WEB_NUM
from proxy_pool.usable_ip import Usable_IP

usable_ip = Usable_IP()

def get_urls(search_keywords: str, usable_ip: Usable_IP):
    ''' Get URLs from Google search results '''
    urls = []
    descriptions = []
    response = GoogleSearch().search(query=search_keywords, num_results=int(SEARCH_WEB_NUM))
    for i in response.results:
        print(i)

def scrape_urls(search_keywords: str):
    return get_urls(search_keywords, usable_ip)

if __name__ == "__main__":
    search_keywords = '阿里巴巴最新的股价'
    scrape_urls(search_keywords)

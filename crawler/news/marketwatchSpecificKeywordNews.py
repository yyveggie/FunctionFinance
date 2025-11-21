import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    无法突破反爬措施。
'''
from urllib.parse import urlencode
from crawler import headless_scrape
from crawler.utils import check_url, check_url_sync, save_urls, save_urls_sync
from data_connection.mongodb import MongoConnection
import re

class MarketWatch_Specific_Keyword_News:
    def __init__(self, keyword):
        self.keyword = keyword
        self.db_connection = MongoConnection('News')
        self.source = "marketwatch.com"

    def fetch_headlines(self, page_num):
        base_url = "https://www.marketwatch.com/search"
        params = {
            'q': self.keyword,
            'ts': '1',
            'tab': 'All News',
            'p': str(page_num),
        }
        url = f"{base_url}?{urlencode(params)}"
        html = headless_scrape.run_sync(urls=[url], raw_content=True)
        return self.parse_headlines(html)

    def parse_headlines(self, html):
        contents = []
        urls = re.findall(r'<a class="link" href="(https://www\.marketwatch\.com/(?:articles|data-news|story)/.*?)"', html[0])
        print('length of urls: {0}'.format(len(urls)))
        filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source=self.keyword)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        if len(filtered_urls) == 0:
            return '当前没有新的链接'
        for url in filtered_urls:
            content = headless_scrape.run_sync(urls=[url])
            contents.append(content)
        data_list = []
        for url, content in zip(filtered_urls, contents):
            data = {'url': url}
            if content:
                data['content'] = content
            else:
                data['content'] = ''
            if any(data.values()):
                print('urls: {}'.format(url))
                print('content: {}'.format(data['content']))
                data_list.append(data)
                self.db_connection.save_data(self.keyword, self.source, data=data)
        # 保存已处理的URL
        processed_urls = [item['url'] for item in data_list]
        save_urls_sync(collection_name=self.source, url_list=processed_urls, source=self.keyword)
        return data_list

    def download(self, max_pages=1):
        '''
        :return
        [
            {
                
            }
        ]
        '''
        all_data = []
        for page_num in range(max_pages):
            data = self.fetch_headlines(page_num)
            all_data.extend(data)
        return all_data

def main(keyword):
    crawler = MarketWatch_Specific_Keyword_News(keyword=keyword)
    return crawler.download(max_pages=2)

if __name__ == "__main__":
    print(main('china'))
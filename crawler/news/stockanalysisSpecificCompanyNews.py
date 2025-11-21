import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 stockanalysis 下载指定公司的新闻。
'''
import json
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from crawler import headless_scrape
from crawler.utils import check_url, check_url_sync, save_urls_sync

class StockAnalysis_Specific_Company_News(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('News')
        self.source = 'stockanalysis.com'
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    def fetch_headlines(self):
        url = f"https://stockanalysis.com/fetch/infinitenews?symbol={self.ticker}&type=s"
        text = self.request_get_sync(url=url, headers=self.headers)
        return self.parse_headlines(text)

    def parse_headlines(self, json_content):
        data = json.loads(json_content)["data"]
        # 提取所有URL并进行筛选
        urls = [item["url"] for item in data]
        print('length of urls: {0}'.format(len(urls)))
        filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source=self.ticker)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))

        if len(filtered_urls) == 0:
            return '当前没有新的链接'

        data_list = [None] * len(data)  # 创建一个与原始数据长度相同的列表，用于存储结果

        for i, item in enumerate(data):
            url = item["url"]
            if url not in filtered_urls:
                data_list[i] = None  # 如果URL被过滤，则将对应位置设为None
                continue

            data = {
                'title': item['title'],
                'create_time': item['time'],
                'url': url
            }

            try:
                content = headless_scrape.run_sync(urls=[url])
                if content and content[0]:
                    data['content'] = content[0]
                else:
                    data['content'] = item['text']
            except Exception as e:
                print(f"Error scraping content for {url}: {e}")
                data['content'] = ''

            if any(data.values()):
                print('url: {}'.format(url))
                print('content: {}'.format(data['content']))
                data_list[i] = data
                self.db_connection.save_data(self.ticker, self.source, data=data)

        # 保存已处理的URL
        processed_urls = [item['url'] for item in data_list if item and 'url' in item]
        save_urls_sync(collection_name=self.source, url_list=processed_urls, source=self.ticker)
        return data_list

    def download(self):
        '''
        :return 
        [
            {
                'title':
                'url':
                'content':
            }
        ]
        '''
        return self.fetch_headlines()

def main(ticker):
    crawler = StockAnalysis_Specific_Company_News(ticker=ticker)
    return crawler.download()

if __name__ == "__main__":
    print(main('MSFT'))
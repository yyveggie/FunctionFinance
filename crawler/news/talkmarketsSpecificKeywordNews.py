import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 talkmarkets.com 下载新闻。
对节点很敏感,而且异步就无法请求到数据。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from crawler import headless_scrape
from lxml import etree
import requests
from crawler.utils import check_url_sync, save_urls_sync

class TalkMarkets_Specific_Keyword_News(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('News')
        self.source = 'talkmarkets.com'
        self.rounds = 1
        self.headers = {
            'User-Agent': UserAgent().random,
        }

    def download(self, delay=0.5):
        '''
        :return
        [
            {
                'title':
                'url':
                'create_time':
                'content':
            }
        ]
        '''
        data_list = []
        for page in range(self.rounds):
            url = f"https://markets.financialcontent.com/talkmarkets/quote/news?CurrentPage={page}&Symbol={self.ticker}"
            text = requests.get(url, headers=self.headers).text
            tree = etree.HTML(text, parser=None)
            titles = tree.xpath('*//div[@class="title"]/a[@target="_blank"]//text()')
            dates = tree.xpath('*//div[@class="title"]/div[@class="date"]/text()')
            urls = tree.xpath('*//div[@class="title"]/a[@target="_blank"]/@href')

            print('length of urls: {0}'.format(len(urls)))
            # 提取所有URL并进行筛选
            filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source=self.ticker)
            print('length of filtered urls: {0}'.format(len(filtered_urls)))
            if len(filtered_urls) == 0:
                return '当前没有新的链接'

            contents = headless_scrape.run_sync(urls=filtered_urls)

            for i, url in enumerate(urls):
                if url not in filtered_urls:
                    continue

                one_sample = {}
                one_sample['title'] = titles[i]
                one_sample['create_time'] = dates[i]
                one_sample['url'] = url
                one_sample['content'] = contents[filtered_urls.index(url)]
                data_list.append(one_sample)

        self.db_connection.save_data(self.ticker, self.source, data_list, ordered=False)
        
        # 保存已处理的URL
        save_urls_sync(collection_name=self.source, url_list=filtered_urls, source=self.ticker)

        return data_list

def main(ticker):
    from config import config
    c = TalkMarkets_Specific_Keyword_News(ticker=ticker, args=config)
    return c.download()

if __name__ == "__main__":
    data = main('BABA')
    print(data)
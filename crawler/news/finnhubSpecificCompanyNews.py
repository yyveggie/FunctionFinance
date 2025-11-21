import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 Finhub API 下载指定公司在某个时间段内（默认当前日期）的新闻。
新闻来源有: Yahoo Finance, Reuters, SeekingAlpha, PennyStocks, MarketWatch, TipRanks
Alliance News, Thefly, TalkMarkets, CNBC, GuruFocus, InvestorPlace

注意:
1.这里使用的是免费的 Finhub API, 其中市场新闻是免费获取的: https://finnhub.io/docs/api/market-news
2.如果超出限制，会收到状态代码为 429 的响应。 
3.除所有计划的限制外，还有每秒 30 次的 API 调用限制。
'''
import os
import finnhub
import pandas as pd
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from datetime import datetime, timedelta
from crawler import headless_scrape

class Finnhub_Specific_Company_News(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.finnhub_client = finnhub.Client(api_key="d01om7hr01qile60sm5gd01om7hr01qile60sm60")
        # self.start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        # self.end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.start_date = '2024-05-01'
        self.end_date = '2024-08-01'
        self.db_connection = MongoConnection('News')
        self.source = 'finnhub.io'

    def download(self):
        '''
        :return
        [
            {
                'create_time':
                'title':
                'source':
                'summary':
                'url':
                'content':
            }
        ]
        '''
        data_dict = {}
        for single_date in pd.date_range(self.start_date, self.end_date).unique():
            tmp_date = single_date.strftime("%Y-%m-%d")
            res = self._gather_one_part(self.ticker, tmp_date, tmp_date)
            if res is not None:
                data_dict[tmp_date] = res
            else:
                return 'Request error.'

        if data_dict:
            filtered_data = self.filter_data(data_dict)
            if isinstance(filtered_data, str):
                return filtered_data
            if filtered_data:
                processed_data = self.process_data(filtered_data)
                if processed_data:
                    self.save_to_db(processed_data)
            else:
                return None
        else:
            return None
        return processed_data

    def _gather_one_part(self, ticker, start_date, end_date):
        try:
            res = self.finnhub_client.company_news(ticker, _from=start_date, to=end_date)
            return res
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def filter_data(self, data_dict):
        filtered_data = {}
        for date, news_list in data_dict.items():
            urls = [item['url'] for item in news_list]
            news = [item for item in news_list if item['url'] in urls]
            if news:
                filtered_data[date] = news
        return filtered_data

    def process_data(self, data_dict, fields_to_remove=['category', 'id', 'image', 'related']):
        data_list = []
        failed_urls = []

        for news_list in data_dict.values():
            for news in news_list:
                if 'datetime' in news:
                    news['create_time'] = datetime.fromtimestamp(news['datetime']).strftime('%Y-%m-%d %H:%M:%S')

                content = headless_scrape.run_sync(urls=[news['url']])

                if content:
                    processed_news = {
                        'create_time': news.get('create_time'),
                        'title': news.get('headline'),
                        'source': news.get('source'),
                        'summary': news.get('summary'),
                        'url': news.get('url'),
                        'content': content[0]
                    }
                    data_list.append(processed_news)
                else:
                    failed_urls.append(news['url'])

        return data_list

    def save_to_db(self, data_list):
        self.db_connection.save_data(collection_name=self.ticker, source=self.source, data=data_list)

def main(ticker):
    from config import config
    crawler = Finnhub_Specific_Company_News(ticker=ticker, args=config)
    return crawler.download()

if __name__ == "__main__":
    print(main('AAPL'))
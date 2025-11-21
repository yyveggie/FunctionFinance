import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from data_connection.mongodb import MongoConnection
from crawler.utils import check_url_sync, save_urls_sync
from datetime import datetime
import finnhub
import os

class Finhub_Specific_Company_News():
    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key="d01om7hr01qile60sm5gd01om7hr01qile60sm60")
        self.db_connection = MongoConnection('News')
        self.source = 'finnhub.io'

    def download(self, delay=0.5):
        '''
        :return
        [
            'create_time':
            'title':
            'url':
            'summary':
        ]
        '''
        news = self.finnhub_client.general_news('general', min_id=0)
        
        # 提取所有URL并进行筛选
        urls = [i['url'] for i in news]
        filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source=self.source)
        print('length of filtered urls: {0}'.format(len(filtered_urls)))
        filtered_urls = urls
        if len(filtered_urls) == 0:
            return '当前没有新的链接'
        
        data_list = []
        for i in news:
            url = i['url']
            if url not in filtered_urls:
                continue
                
            date_time = datetime.fromtimestamp(i['datetime'])
            formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
            data = {
                'create_time': formatted_date_time,
                'title': ''.join([i['headline']]),
                'url': url,
                'summary': ''.join([i['summary']])
            }
            data_list.append(data)
        
        self.db_connection.save_data('public', self.source, data_list, ordered=False)
        
        # 保存已处理的URL
        save_urls_sync(collection_name=self.source, url_list=filtered_urls, source=self.source)
        
        return data_list

def main():
    c = Finhub_Specific_Company_News()
    return c.download()

if __name__ == "__main__":
    from pprint import pprint
    pprint(main())
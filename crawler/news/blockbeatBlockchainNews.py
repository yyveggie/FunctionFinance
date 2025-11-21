import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

'''
从 theblockbeats 的 API 下载区块链相关的最新新闻:
https://www.theblockbeats.info/
https://github.com/BlockBeatsOfficial/RESTful-API
'''
import json
from datetime import datetime
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from crawler.significance_score import ArticleScorer
from crawler.text_time_knowledge_graph import StockKnowledgeExtractor
from crawler.utils import check_url_sync, save_urls_sync

class BlockBeats_News(Usable_IP):
    def __init__(self, args=None):
        super().__init__(args)
        self.scorer = ArticleScorer()
        self.source = "blockbeats.com"
        self.rounds = 1
        self.headers = {
            'user-agent': UserAgent().random,
            'authority': 'api.theblockbeats.news',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        host = "localhost"
        knowledge_name = "Blockchain"
        knowledge_port = 27018
        raw_data_name = "News"
        raw_data_port = 27017
        self.knowledge = StockKnowledgeExtractor(knowledge_name, host, knowledge_port)
        self.db_connection = MongoConnection(raw_data_name, host, raw_data_port)

    def download(self):
        """
        :return [
            {
                'content': 
                'url':
                'title':
                'create_time':
                'significance_score':
            }
        ]
        """
        all_data = []
        for i in range(self.rounds):
            params = {
                'page': i + 1,
                'size': 20,
                'type': 'push'
            }
            url = "https://api.theblockbeats.news/v1/open-api/open-flash"
            response_text = self.request_get_sync(url=url, headers=self.headers, params=params)
            if response_text:
                res = json.loads(response_text)
                data = res["data"]["data"]
                urls = [item['link'] for item in data]
                print('length of urls: {0}'.format(len(urls)))
                filtered_urls = check_url_sync(collection_name=self.source, url_list=urls, source='blockchain')
                print('length of filtered urls: {0}'.format(len(filtered_urls)))

                if len(filtered_urls) > 0:
                    data = [item for item in data if item['link'] in filtered_urls]
                    articles = [item['content'] for item in data]
                    scores = self.scorer.score_articles(articles)
                    knowledges = self.knowledge.extract_and_save(articles)
                    for item, score, knowledge in zip(data, scores, knowledges):
                        del item['id']
                        del item['pic']
                        del item['url']
                        item['create_time'] = datetime.fromtimestamp(int(item['create_time'])).strftime('%Y-%m-%d %H:%M:%S')
                        value = item.pop('link')
                        item['url'] = value
                        item['score'] = score
                        item['knowledge'] = knowledge

                    all_data.extend(data)
                    save_urls_sync(collection_name=self.source, url_list=filtered_urls, source='blockchain')
                else:
                    print('当前没有新的链接')
            else:
                print(f"Failed to fetch data for round {i + 1}")

        if all_data:
            self.db_connection.save_data("blockchain", self.source, all_data)
            return all_data
        else:
            return {}

def main():
    c = BlockBeats_News()
    return c.download()

if __name__ == "__main__":
    print(main())
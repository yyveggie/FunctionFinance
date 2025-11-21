import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 mxnzp 的 API 下载最新新闻: https://www.mxnzp.com/doc/detail?id=12
    每一页包含十条新闻, 包括内容。
    这个最新新闻以中文为主, 包含多家新闻媒体。
    可选择的新闻类型有:
        532: 新闻; 533: 娱乐; 534: 体育; 535: 财经; 536: 军事; 537: 科技; 538: 手机; 539: 数码; 540: 时尚; 541: 游戏; 542: 体育; 543: 健康; 544: 旅游; 545: 视频; 546: 头条; 547: 精选.
    注意:
        1. 有次数限制, 更多需要充值, 关注小程序: 电点科技
'''
import os
import requests
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from tqdm import tqdm
import pandas as pd


class Mxnzp_News(Usable_IP):
    def __init__(self, args=None):
        super().__init__(args)
        self.appid = os.environ.get('Mxnzp_APPID')
        self.appsecret = os.environ.get('Mxnzp_APPSECRET')
        self.db_connection = MongoConnection('News')
        self.dataframe = pd.DataFrame()
        self.source = "Mxnzp"
        self.rounds = 1

    def download(self):
        '''
        :return 
        [
            {
                'title':
                'create_time':
                'content':
            }
        ]
        '''
        url = "https://www.mxnzp.com/api/news/list/v2"
        data_list = []
        for i in tqdm(range(self.rounds), desc="Downloading by page.."):
            data = {
                "title": [],
                "digest": [],
                "content": [],
                "postTime": [],
                "source": [],
            }
            params = {
                # 532: 新闻; 533: 娱乐; 534: 体育; 535: 财经; 536: 军事; 537: 科技; 538: 手机; 539: 数码; 540: 时尚; 541: 游戏; 542: 体育; 543: 健康; 544: 旅游; 545: 视频; 546: 头条; 547: 精选.
                'typeId': 535,
                'page': i+1
            }
            headers = {
                'user-agent': UserAgent().random,
                'app_id': self.appid,
                'app_secret': self.appsecret,
            }
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                res = response.json()
                res = res["data"]
                for j in res:
                    data = {}
                    data["title"] = j["title"]
                    data["digest"] = j["digest"]
                    data["create_time"] = j["postTime"]
                    data["content"] = self._get_content(j["newsId"])
                    data["source"] = j["source"]
                    data_list.append(data)
            else:
                data = None
        self.db_connection.save_data('public', self.source, data_list)
        return data_list

    def _get_content(self, newsId):
        content = ''
        url = "https://www.mxnzp.com/api/news/details/v2"
        params = {
            'newsId': newsId,
        }
        headers = {
            'user-agent': UserAgent().random,
            'app_id': self.appid,
            'app_secret': self.appsecret,
        }
        response = requests.get(url=url, headers=headers, params=params)
        try:
            for j in response.json()["data"]["items"]:
                content = content + j['content']
        except KeyError:
            print("请求频率过快。")
        return content

def main():
    c = Mxnzp_News()
    return c.download()

if __name__ == "__main__":
    print(main())

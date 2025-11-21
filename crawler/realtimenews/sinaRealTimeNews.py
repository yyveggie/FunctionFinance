import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从新浪下载实时新闻。
    每60秒更新一次。
'''
import json
import time
import re
import requests
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from datetime import datetime
from ast import literal_eval
from fake_useragent import UserAgent


class Sina_Real_Time_News(Usable_IP):
    def __init__(self, args=None):
        super().__init__(args)
        self.url = "https://zhibo.sina.com.cn/api/zhibo/feed?callback=jQuery1112016038192308276655_1692779772117&page=1&page_size=20&zhibo_id=152&tag_id=0&dire=f&dpc=1&pagesize=20&id=3217596&type=0&_=1692779772121"
        self.db_connection = MongoConnection('Real_Time_News')
        self.source = "sina"
        self.headers = {
            "user-agent": UserAgent().random,
            "referer": "https://finance.sina.com.cn/",
            'authority': 'zhibo.sina.com.cn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            # 'cookie': 'UOR=www.bing.com,finance.sina.com.cn,; SINAGLOBAL=194.195.90.129_1680769549.686865; __bid_n=188519d484d10f83524207; SUB=_2AkMTKQ1Uf8NxqwJRmP8dzWzrZY1yyQDEieKldfyPJRMyHRl-yD9vqhIttRB6OKkju7WAVux37Ppt57zNF4oW7M9gKrOi; FPTOKEN=eatgEPkVLierpG9ulUn0Ih8ESUG5vZCeD+h6b1/ZZtfIpiyD1DxzJBynt+YSAiFpfKFOBfV9SQfSi/TRGRp5wJ99iVbcGY6VVin0lqifTAZocYuJ5qcPmxWVzJjJIL1C7rTFA7dVT9PL9kW7ineJj7rQvmC6VzYVpU3E6FDts1LB3qA77auV9jdB3b1fmqAk25uHMah2GyRs65OjVZmWsI+jps1BiW/P95XH6NyP0imgqxEcP6Jf8Rwn1r1Sv24sYAL07j5rMgwbRNgg43g06TYFO/E/RKDfzuQOZKA9We18/TW63SnB6nF2PeDfQmN4sTlespsWtmkYwflxAWdCJS+qDJaCtsjHmwhwIcPrKqn7RVDqhtvtLlyAO4h+eRwzTuQdfFsktKarR7t86oYIeg==|WbREr3vZ5aqhrJ2WwbnjGF3TOqFpULVUr1/fDs5Gb8M=|10|d3107535afd5c1cd8538de4db42c9751; U_TRS1=00000024.837e53369.64e6e49e.d79c9b35; FSINAGLOBAL=194.195.90.129_1680769549.686865; Hm_lvt_b82ffdf7cbc70caaacee097b04128ac1=1691588338,1693115435,1693642243; Apache=45.142.158.43_1693806987.618733; ULV=1693807007124:18:6:2:45.142.158.43_1693806987.618733:1693806979698',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }

    def get_news(self):
        res = requests.get(self.url, headers=self.headers)
        res = res.text
        res = re.findall('"rich_text":"(.*?)","multimedia":', res, re.S)
        news = [literal_eval(f'"{i}"') for i in res]
        return news

    def get_latest_news(self):
        current_news = self.get_news()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        news_data = {'Timestamp': timestamp, 'News': current_news}
        return json.dumps(news_data, ensure_ascii=False)

    def main(self):
        last_news = []
        while True:
            current_news = self.get_news()
            new_news = [news for news in current_news if news not in last_news]
            if new_news:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_data = {'Timestamp': [timestamp]
                            * len(new_news), 'News': new_news}
                for news in new_news:
                    print(f"{timestamp}: {news}")
                self.db_connection.save_data("sina", self.source, new_data)
                last_news = current_news
            time.sleep(60)  # Check for news updates every minute


if __name__ == "__main__":
    from config import config
    c = Sina_Real_Time_News(config)
    c.main()

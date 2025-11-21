import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从 whalewisdom 下载指定股票的最新股东持有信息。
'''
import re
import json
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent

class Whalewisdom_Specific_Company_Shareholder(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Shareholder')
        self.source = "whalewisdom.com"
        self.rounds = 1
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cookie': '_ga=GA1.1.923099795.1717141328; _Whalewisdom_session=a45dfbe6e3103b2f3102a73df5769573; search_filter=6; _ga_W3YC81ZC30=GS1.1.1717141328.1.1.1717143376.0.0.0',
            'priority': 'u=1, i',
            'referer': 'https://whalewisdom.com/stock/TSLA',
            'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
        }
    
    def _get_stock_id(self):
        url = 'https://whalewisdom.com/stock/' + self.ticker
        string = self.request_get_sync(url, headers=self.headers)
        match = re.search(r'null,false', string)
        if match:
            # 获取 "false,null" 后面的内容
            substring = string[match.end():]
            # 使用正则表达式按逗号分隔子字符串，并抽取两个逗号之间的内容
            elements = re.findall(r'(?<=,)[^,]+(?=,)', substring)
            # 取最近的十个元素
            recent_elements = elements[:10]
            # 逐个判断元素，找到第一个连续的非零数字
            for element in recent_elements:
                if element.strip().startswith('"') and element.strip().endswith('"'):
                    # 如果元素以引号开头和结尾，跳过
                    continue
                if re.match(r'^\d{2,}$', element.strip()):
                    # 如果元素是连续的数字且不是0，打印并退出循环
                    stock_id = element.strip()
                    return stock_id
            else:
                check = "未找到匹配的数字"
        else:
            check = "未找到以 'null,false' 开始的部分"
        if check == "未找到以 'null,false' 开始的部分":
            match = re.search(r'false,null', string)
            if match:
                # 获取 "false,null" 后面的内容
                substring = string[match.end():]
                # 使用正则表达式按逗号分隔子字符串，并抽取两个逗号之间的内容
                elements = re.findall(r'(?<=,)[^,]+(?=,)', substring)
                # 取最近的十个元素
                recent_elements = elements[:10]
                print(recent_elements)
                # 逐个判断元素，找到第一个连续的非零数字
                for element in recent_elements:
                    if element.strip().startswith('"') and element.strip().endswith('"'):
                        # 如果元素以引号开头和结尾，跳过
                        continue
                    if re.match(r'^\d{2,}$', element.strip()):
                        # 如果元素是连续的数字且不是0，打印并退出循环
                        stock_id = element.strip()
                        return stock_id
                else:
                    print("未找到匹配的数字")
            else:
                print("未找到以 'false,null' 开始的部分")
        
    def download(self):
        stock_id = self._get_stock_id()
        data_list = []
        url = 'https://whalewisdom.com/stock/holdings'
        for i in range(self.rounds):
            params = {
                'id': str(stock_id),
                'q1': '-1',
                'change_filter': '',
                'mv_range': '',
                'perc_range': '',
                'rank_range': '',
                'sc': 'true',
                'sort': 'current_shares',
                'order': 'desc',
                'offset': str(i * 50),
                'limit': '50',
            }
            resp = self.request_get_sync(url, params=params, headers=self.headers)
            data_temp = json.loads(resp)['rows']
            data_list = data_list + data_temp
        self.db_connection.save_data(self.ticker, self.source, data_list)
        return data_list

def main(ticker):
    c = Whalewisdom_Specific_Company_Shareholder(ticker)
    return c.download()

if __name__ == "__main__":
    from pprint import pprint
    pprint(main('TSLA'))
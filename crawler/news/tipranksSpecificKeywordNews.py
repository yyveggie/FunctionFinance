import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从https://www.tipranks.com下载关键词的新闻。
'''
import re
import time
import json
import pandas as pd
from lxml import etree
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from crawler.utils import check_url_sync, save_urls_sync

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class TipRanks_Specific_Keyword_News(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.dataframe = pd.DataFrame()
        self.db_connection = MongoConnection('News')
        self.source = 'tipranks.com'
        self.rounds = 1

    def download(self, delay=0.5):
        url = "https://www.tipranks.com/api/news/posts"
        headers = {
            'authority': 'www.tipranks.com',
            'User-Agent': UserAgent().random
        }
        for r in range(self.rounds):
            params = {
                'page': r + 1,
                'per_page': 30,
                'search': self.keyword,
            }
            try:
                res = self.request_get_sync(url=url, headers=headers, params=params)
            except:
                pass
            try:
                res = json.loads(res)
                tmp = pd.DataFrame(res['data'])

                def get_content_url(x):
                    if len(x) > 0:
                        return x[0]
                    return None

                content_urls = tmp["description"].apply(lambda x: re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', str(x))).apply(get_content_url).tolist()
                print('length of urls: {0}'.format(len(content_urls)))
                filtered_urls = check_url_sync(collection_name=self.source, url_list=content_urls, source=self.keyword)
                print('length of filtered urls: {0}'.format(len(filtered_urls)))
                filtered_urls = content_urls
                tmp["content_url"] = [url if url in filtered_urls else None for url in content_urls]

                def get_content(row):
                    if row['content_url']:
                        content = self._get_content(row['content_url']) 
                        if isinstance(content, list):
                            return ''.join(item.strip() for item in content)
                        else:
                            return None
                    return None

                tmp["content"] = tmp.apply(get_content, axis=1)
                
                # 过滤掉被过滤URL对应的行
                tmp = tmp[tmp["content_url"].notnull()]

                self.dataframe = pd.concat([self.dataframe, tmp])
                
                # 保存已处理的URL
                processed_urls = tmp["content_url"].tolist()
                save_urls_sync(collection_name=self.source, url_list=processed_urls, source=self.keyword)
                
            except Exception as e:
                print(f"Error in round {r}: {e}")
            time.sleep(delay)
        
        columns_to_drop = ['_id', 'author', 'category', 'description', 'image', 'isLocked',
                           'lockType', 'slug', 'sticky', 'thumbnail', 'topics', 'timeAgo', 
                           'time', 'badge', 'id', 'link', 'stocks']
        columns_to_drop = [col for col in columns_to_drop if col in self.dataframe.columns]                   
        dataframe = self.dataframe.drop(columns_to_drop, axis=1)
        dict_data = dataframe.to_dict(orient='records')
        self.db_connection.save_data(self.keyword, self.source, dict_data, ordered=False)
        return dict_data

    def _get_content(self, content_url):
        headers = {
            'authority': 'blog.tipranks.com',
            'user-agent': UserAgent().random
        }
        try:
            res = self.request_get_sync(url=content_url, headers=headers)
            html = etree.HTML(res, parser=None)
            content = html.xpath(
                '/html/body/div[1]/div/div/div/div[1]/article/div[3]//text()')
            return content
        except Exception as e:
            print(f"Error while fetching content: {e}")
            return None

def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_en.json")

    # 读取 stocks_en.json 文件
    try:
        with open(stocks_file_path, "r") as file:
            data = json.load(file)
            keywords = eval(data["keywords"])
    except FileNotFoundError:
        print(f"未找到文件: {stocks_file_path}")
        return []

    # 初始化结果记录
    results = []

    # 逐个关键词串行处理
    for keyword in keywords:
        print(f"开始处理关键词: {keyword}")
        c = TipRanks_Specific_Keyword_News(keyword)

        try:
            data = c.download()
            print(f"关键词: {keyword} 爬取成功，获取到 {len(data)} 条数据。")
            results.append((keyword, "成功", len(data)))
        except Exception as e:
            print(f"关键词: {keyword} 爬取失败，错误信息: {e}")
            results.append((keyword, "失败", 0))

    # 输出总结
    print("\n爬取总结：")
    for r in results:
        print(f"关键词: {r[0]}, 状态: {r[1]}, 数据条数: {r[2]}")

    return results

if __name__ == "__main__":
    main()
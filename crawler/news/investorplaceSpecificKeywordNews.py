import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
从https://investorplace.com下载关键词的新闻。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from crawler.utils import check_url_sync, save_urls_sync
from fake_useragent import UserAgent
from lxml import etree
import re
import json

class InvestorPlace_Specific_Keyword_News(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.db_connection = MongoConnection('News')
        self.source = "investorplace.com"
        self.rounds = 1
        self.headers = {
            "User-Agent": UserAgent().random,
            'authority': 'investorplace.com',
        }

    def download(self):
        '''
        :return 
        [
            {
                'title':
                'url':
                'content':
                'create_time':
            }
        ]
        '''
        url = 'https://investorplace.com/search/'
        all_links = []
        all_titles = []
        all_published_dates = []
        
        for page in range(self.rounds):
            params = {
                'q': self.keyword,
                "pg": page,
                "category": "all",
                "sort": "date"
            }
            text = self.request_get_sync(url=url, params=params, headers=self.headers)
            tree = etree.HTML(text, parser=None)
            titles = tree.xpath('//*[@class="subcat-post-row"]//h2/a/text()')
            titles = [title.strip() for title in titles]
            links = tree.xpath('//*[@class="subcat-post-row"]//h2/a/@href')
            published_date = tree.xpath('//*[@class="subcat-post-row"]//time/@datetime')
            
            all_links.extend(links)
            all_titles.extend(titles)
            all_published_dates.extend(published_date)
            
        print('length of urls: {0}'.format(len(all_links)))
        filtered_links = check_url_sync(collection_name=self.source, url_list=all_links, source=self.keyword)
        print('length of filtered links: {0}'.format(len(filtered_links)))
        filtered_links = all_links
        if len(filtered_links) == 0:
            return []
        
        data_list = []
        for i, link in enumerate(all_links):
            if link in filtered_links:
                content = self._get_content(link)
                one_sample = {
                    "title": all_titles[i],
                    "url": link,
                    "create_time": all_published_dates[i],
                    "content": content
                }
                data_list.append(one_sample)
        
        self.db_connection.save_data(self.keyword, self.source, data_list)
        save_urls_sync(collection_name=self.source, url_list=filtered_links, source=self.keyword)
        return data_list

    def _get_content(self, url):
        res = self.request_get_sync(url, headers=self.headers)
        tree = etree.HTML(res, parser=None)
        content = tree.xpath('//article//text()')
        content_str = ' '.join(content)
        cleaned_content = re.sub(r'[\n\t]+', ' ', content_str)
        cleaned_content = cleaned_content.strip()
        return cleaned_content

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
        c = InvestorPlace_Specific_Keyword_News(keyword)

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
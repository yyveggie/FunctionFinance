import os
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    爬取微博指定关键词的微博帖子, 每一页十条。
'''
import re
import json
import time
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
import pandas as pd
from lxml import etree
from tqdm import tqdm
from fake_useragent import UserAgent

class Weibo_Specific_Keyword_Post(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.dataframe = pd.DataFrame()
        self.db_connection = MongoConnection('Post')
        self.source = 'weibo.com'
        self.rounds = 5

    def download(self):
        for r in tqdm(range(self.rounds), desc="Downloading by page.."):
            page = r+1
            self._gather_one_page(page)
        data_list = self.dataframe.to_dict(orient='records')
        self.db_connection.save_data(
            self.keyword, self.source, data_list, ordered=False)
        return data_list

    def _gather_one_page(self, page, delay=0.5):
        headers = {
            "User-Agent": UserAgent().random
        }
        params = {
            "containerid": f"100103type=61&q={self.keyword}&t=",
            "page_type": "searchall",
            "page": page
        }
        url = f"https://m.weibo.cn/api/container/getIndex"
        resp = self.request_get_sync(url, headers=headers, params=params)
        res = json.loads(resp)
        res = res["data"]["cards"]
        res = pd.DataFrame(res)
        pbar = tqdm(
            total=res.shape[0], desc="Processing the text content and downloading the full passage...")
        res[["content_short", "content"]] = res.apply(
            lambda x: self._process_text(x, pbar, delay), axis=1, result_type="expand")
        self.dataframe = pd.concat([self.dataframe, res])

    def _process_text(self, x, pbar, delay=0.5):
        if isinstance(x["mblog"], dict) and "text" in x["mblog"]:
            text = x["mblog"]["text"]
            text = etree.HTML(text)  # type: ignore
            content_short = text.xpath(".//text()")
            content_short = ''.join(content_short)
            link = text.xpath('.//a/@href')
            link = [l for l in link if "status" in l]
            if len(link) > 0:
                base_url = "https://m.weibo.cn/"
                url_new = base_url + link[0]
                headers = {
                    "User-Agent": UserAgent().random
                }
                resp = self.request_get_sync(url_new, headers=headers)
                if resp is None:
                    content = content_short
                else:
                    res = etree.HTML(resp)  # type: ignore
                    scripts = res.xpath('//script')
                    content = scripts[2].xpath("text()")
                    pattern = re.compile('"text": "(.+),\\n')
                    result = pattern.findall(content[0])
                    content = etree.HTML(result[0])  # type: ignore
                    content = content.xpath("//text()")
                    content = ''.join(content)
            else:
                content = content_short
        else:
            content_short = ""
            content = ""

        pbar.update(1)
        time.sleep(delay)
        return content_short, content

def main():
    # 获取项目根目录
    project_root = rootutils.find_root(indicator=".project-root")
    stocks_file_path = os.path.join(project_root, "stocks_cn.json")

    # 读取 stocks_cn.json 文件
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
        c = Weibo_Specific_Keyword_Post(keyword)

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
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    仅对 A 股、港股上市公司有效。
    从巨潮网下载指定公司的公告, 但无法选择公告类型。
'''
import re
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from bson.binary import Binary
from fake_useragent import UserAgent
from proxy_pool.usable_ip import Usable_IP
from data_connection.mongodb import MongoConnection


class Juchao_Specific_Company_Random_Announcement(Usable_IP):
    def __init__(self, company, start_date, end_date, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.rounds = 1
        self.db_connection = MongoConnection('Announcement')
        self.source = "juchao"

    def _get_headers(self):
        return {
            "Referer": "http://www.cninfo.com.cn/new/disclosure/",
            "User-Agent": UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def download(self, delay=0.5):
        url = f"http://www.cninfo.com.cn/new/fulltextSearch/full"
        headers = self._get_headers()
        pbar = tqdm(total=self.rounds, desc="Downloading by pages...")
        for page in range(self.rounds):
            params = {
                "searchkey": self.company,
                "sdate": self.start_date,
                "edate": self.end_date,
                "isfulltext": "false",
                "sortName": "pubdate",
                "sortType": "desc",
                "pageNum": page + 1,
            }
            res = self._request_get(url=url, headers=headers, params=params)
            if res.json()["totalAnnouncement"] > 0:
                announcements = res.json()["announcements"]
                data = [{
                    'time': datetime.fromtimestamp(a["announcementTime"] / 1000),
                    'short_title': a["shortTitle"],
                    'download_url': "http://www.cninfo.com.cn/new/announcement/download?bulletinId=" + re.search(r'(\d+)\.PDF', a["adjunctUrl"]).group(1)
                } for a in announcements if announcements]
                dataframe = pd.concat([self.dataframe, pd.DataFrame(data)])
                for a in announcements:
                    self.download_pdf(
                        a["adjunctUrl"], a["shortTitle"], self.company)
                pbar.update(1)
            else:
                continue
            time.sleep(delay)
        return dataframe

    def download_pdf(self, adjunctUrl, short_title, stock):
        url = "http://www.cninfo.com.cn/new/announcement/download"
        announcementId = re.search(r'(\d+)\.PDF', adjunctUrl).group(1)
        params = {"bulletinId": announcementId}
        headers = self._get_headers()
        try:
            res = self._request_get(url=url, headers=headers, params=params)
            try:
                binary_pdf = Binary(res.content)
                pdf_document = {
                    "stock": [stock],
                    "title": [short_title],
                    "file": [binary_pdf]
                }
                self.db_connection.save_data(stock, self.source, pd.DataFrame(
                    pdf_document).to_dict(orient='split'))
                print(f'{stock}_{short_title} has been saved to MongoDB')
            except Exception as e:
                print(f'Save to MongoDB failed: {e}')
        except Exception as e:
            print(f'Download failed: {e}')


def main():
    from config import config
    c = Juchao_Specific_Company_Random_Announcement(
        company='中国平安', start_date='2024-02-01', end_date='2024-02-09', args=config)
    print(c.download())


if __name__ == "__main__":
    main()

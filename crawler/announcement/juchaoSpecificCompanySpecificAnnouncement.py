import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    仅对 A 股上市公司有效。
    从巨潮网下载指定公司的特定公告。
'''
import time
import re
from data_connection.mongodb import MongoConnection
from bson.binary import Binary
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime
from tqdm import tqdm
import pandas as pd


class Juchao_Specific_Company_Specific_Announcement(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.companies = [item[0] for item in args["company_cn"]]
        self.announcement_type = args["announcement_type"][0]
        self.start_date = args["start_date"][0]
        self.end_date = args["end_date"][0]
        self.rounds = 2
        self.db_connection = MongoConnection('Announcement')
        self.source = "juchao"

    def download(self, delay=0.5):
        company_data = {}
        for company in self.companies:
            self.company = company
            stock_code, orgId, plate = self.get_orgId_and_stock_code()
            dataframe = self.get_announcement(stock_code, orgId, plate, delay)
            if dataframe.empty:
                company_data[company] = None
            else:
                company_data[company] = dataframe.to_dict(orient='split')
        return company_data

    def get_orgId_and_stock_code(self):
        url = "http://www.cninfo.com.cn/new/information/topSearch/detailOfQuery"
        headers = {
            "Referer": "http://www.cninfo.com.cn/",
            "User-Agent": UserAgent().random,
            "Host": "www.cninfo.com.cn",
            "Origin": "http://www.cninfo.com.cn",
            "Proxy-Connection": "keep-alive",
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        }
        data = {
            "keyWord": self.company,
            "maxSecNum": 10,
            "maxListNum": 5
        }
        res = self._request_post(
            url=url, headers=headers, data=data, json_data=None)
        res_json = res.json()
        stockcode_and_orgId_dict = res_json["keyBoardList"]
        if len(stockcode_and_orgId_dict) == 0:
            print("Oops! The current stock does not have corresponding content. Please check whether it is listed on the Chinese Mainland exchanges.")
        else:
            for i in stockcode_and_orgId_dict:
                # print(i)
                if i["category"] == "A股" or i["category"] == "港股":
                    print(i)
                    stock_code = i["code"]
                    orgId = i["orgId"]
                    plate = i["plate"]
                else:
                    continue
        # print(stock_code, orgId, plate)
        return stock_code, orgId, plate

    def get_announcement(self, stock_code, orgId, plate, delay):
        url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        pbar = tqdm(total=self.rounds, desc="Downloading by pages...")
        dataframe = pd.DataFrame()
        titles = []
        times = []
        download_urls = []
        page_size = 30
        num = page_size * self.rounds
        for i in range(self.rounds):
            time.sleep(delay)
            if num > 0:
                data = {
                    "stock": str(stock_code) + ',' + str(orgId),
                    "tabName": "fulltext",
                    "pageSize": page_size,
                    "pageNum": i + 1,
                    # "column": "szse",
                    "category": self.announcement_type,
                    "plate": plate,
                    "seDate": self.start_date + "~" + self.end_date,
                    "searchkey": None,
                    "secid": None,
                    "sortName": None,
                    "sortType": None,
                    "isHLtitle": "true"
                }
                headers = {
                    "Referer": f"http://www.cninfo.com.cn/new/disclosure/stock?tabName=data&orgId={orgId}&stockCode={stock_code}",
                    "User-Agent": UserAgent().random
                }
                try:
                    res = self._request_post(
                        url=url, data=data, headers=headers, json_data=None)
                except Exception as e:
                    print(f"Oops! Post Error: {e}")
                    return None
                res_json = res.json()
                totalAnnouncement = res_json["totalAnnouncement"]
                if totalAnnouncement > 0:
                    content_list = res_json["announcements"]
                    if content_list is not None:
                        for i in range(len(content_list)):
                            title = content_list[i]["announcementTitle"]
                            titles.append(title)
                            time_ = content_list[i]["announcementTime"] / 1000
                            times.append(datetime.fromtimestamp(time_))
                            adjunctUrl = content_list[i]["adjunctUrl"]
                            self.download_pdf(adjunctUrl, title)
                            download_urls.append(
                                "http://www.cninfo.com.cn/new/announcement/download?bulletinId=" + re.search(r'(\d+)\.PDF', adjunctUrl).group(1))
                        data = {
                            'title': titles,
                            'time': times,
                            'download_url': download_urls
                        }
                        dataframe = pd.concat([dataframe, pd.DataFrame(data)])
                        num = num - page_size * \
                            (self.rounds - i + 1) + totalAnnouncement
                    pbar.update(1)
            else:
                print(
                    f'There are no announcements of type {self.announcement_type} reported during the period from {self.start_date} to {self.end_date}')
                num = - 1
        return dataframe

    def download_pdf(self, adjunctUrl, title):
        url = "http://www.cninfo.com.cn/new/announcement/download"
        announcementId = re.search(r'(\d+)\.PDF', adjunctUrl).group(1)
        params = {"bulletinId": announcementId}
        headers = {
            "Referer": "http://www.cninfo.com.cn/new/disclosure/",
            "User-Agent": UserAgent().random,
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
        }
        try:
            res = self._request_get(url=url, headers=headers, params=params)
            pdf = res.content
            binary_pdf = Binary(pdf)
            pdf_document = {
                "stock": self.company,
                "title": title,
                "file": binary_pdf
            }
            self.db_connection.save_data(self.company, self.source, pd.DataFrame(
                pdf_document).to_dict(orient='split'))
            print(self.company + '_' + f'{title} has been saved to MongoDB')
        except Exception as e:
            print(f'Download or save to MongoDB failed: {e}')


if __name__ == "__main__":
    from config import config
    c = Juchao_Specific_Company_Specific_Announcement(config)
    print(c.download())

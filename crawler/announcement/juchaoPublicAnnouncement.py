import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    仅对 A 股和港股上市公司有效。
    爬取不同行业, 不同类别的公告, 但不能指定公司。
'''
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime
from tqdm import tqdm
import time
import pandas as pd
from data_connection.mongodb import MongoConnection
from bson.binary import Binary


class Juchao_Public_Announcement(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.public_announcement_type = args["public_announcement_type"][0]
        self.column = args['column'][0]
        self.plate = args['plate'][0]
        self.tabName = 'fulltext'
        try:
            self.trade = args['trade'][0]
        except:
            self.trade = None
        self.start_date = args["start_date"][0]
        self.end_date = args["end_date"][0]
        self.announcement_type = args['announcement_type'][0]
        try:
            self.fund_company = args['fund_company'][0]
        except:
            self.fund_company = None
        self.db_connection = MongoConnection('Announcement')
        if self.public_announcement_type == '持续督导':
            self.tabName = 'supervise'
        elif self.public_announcement_type == "调研":
            self.tabName = 'relation'
        else:
            self.tabName = 'fulltext'
        self.source = 'juchao'
        self.rounds = 1
        # if self.public_announcement_type == "A股":
        #     self.column = '深市'    # 深市 or 深主板 or 创业板 or 沪市 or 沪主板 or 科创板 or 北交所
        #     self.announcement_type = "权益分派"
        #     self.trade = '金融业'   # 农、林、牧、渔业 or 采矿业 or 制造业 or 电力、热力、燃气及水生产和供应业 or 建筑业 or 批发和零售业 or 交通运输、仓储和邮政业 or 住宿和餐饮业 or 信息传输、软件和信息技术服务业 or 金融业 or 房地产业 or 租赁和商务服务业 or 科学研究和技术服务业 or 水利、环境和公共设施管理业 or 居民服务、修理和其他服务业 or 教育 or 卫生和社会工作 or 文化、体育和娱乐业 or 综合
        #     self.plate = '深市'
        # elif self.public_announcement_type == "港股":
        #     self.column = '港股'
        #     self.plate = '港主板'   # 港主板 or 港创业板
        # elif self.public_announcement_type == "三板":
        #     self.column = '三板'
        #     self.announcement_type = '临时公告'  # 临时公告 or 定期公告 or 中介机构公告 or 持续信息披露 or 首次信息披露
        #     self.plate = '新三板'   # 新三板 or 老三板
        #     self.trade = '金融业'
        # elif self.public_announcement_type == "基金":
        #     self.column = '基金'
        #     self.announcement_type = '招募设立'  # 招募设立 or 说明书更新 or 年报 or 中报 or 季报 or 净值 or 投资组合 or 申购赎回 or 基金费率 or 销售渠道 or 分红 or 高管及基金经理 or 持有人大会 or 基本信息变更 or 其他
        #     self.secid = '富国基金'
        # elif self.public_announcement_type == "债券":
        #     self.column = '债券'
        #     self.announcement_type = '债券发行上市'  # 债券发行上市 or 债券定期公告 or 债券付息公告 or 债券到期兑付停止交易公告 or 债券其他公告
        #     self.plate = '沪市债券'  # 深市债券 or 沪市债券
        # elif self.public_announcement_type == "监管":
        #     self.column = '监管'
        #     self.announcement_type = '停复牌'  # 停复牌 or 业务通知 or 批评处罚及公开谴责 or 交易风险提示 or 其他
        #     self.plate = '深交所'
        # elif self.public_announcement_type == "调研":
        #     self.column = '调研'
        #     self.trade = '金融业'
        #     self.plate = '深主板'
        #     self.tabName = 'relation'
        # elif self.public_announcement_type == '持续督导':
        #     self.column = '深市' # 只能选择'深市'
        #     self.plate = '深主板'
        #     self.announcement_type = '保荐机构持续督导意见'  # 保荐机构持续督导意见 or 财务顾问持续督导意见
        #     self.trade = '金融业'
        #     self.tabName = 'supervise'

    def download(self, delay=0.5):
        url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        headers = {
            "Referer": "http://www.cninfo.com.cn/",
            "User-Agent": UserAgent().random,
            "Host": "www.cninfo.com.cn",
            "Origin": "http://www.cninfo.com.cn",
            "Proxy-Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Cache-Control': 'max-age=0',
        }
        pbar = tqdm(total=self.rounds, desc="Downloading by pages...")
        titles, times, secNames, download_urls, pdfs = [], [], [], [], []
        page_size = 30
        num = page_size * self.rounds
        for i in range(self.rounds):
            if num > 0:
                data = {
                    "pageNum": i + 1,
                    "pageSize": page_size,
                    "column": self.column if self.column else None,
                    "tabName": self.tabName,
                    "plate": self.plate if self.plate else None,
                    "stock": None,
                    "searchkey": None,
                    "secid": self.fund_company,
                    "category": self.announcement_type.replace(";", '') if self.announcement_type else None,
                    "trade": self.trade if self.trade else None,
                    "seDate": self.start_date + "~" + self.end_date,
                    "sortName": None,
                    "sortType": None,
                    "isHLtitle": "true"
                }
                try:
                    res = self._request_post(
                        url=url, data=data, headers=headers)
                except Exception as e:
                    print(f"Post error: {e}")
                    return None
                res_json = res.json()
                totalAnnouncement = res_json["totalAnnouncement"]
                if totalAnnouncement > 0:
                    content_list = res_json["announcements"]
                    if content_list is not None:
                        for i in range(len(content_list)):
                            secName = content_list[i]["secName"]
                            secNames.append(secName)
                            title = content_list[i]["announcementTitle"]
                            titles.append(title)
                            time_ = content_list[i]["announcementTime"] / 1000
                            times.append(datetime.fromtimestamp(time_))
                            announcementId = content_list[i]["announcementId"]
                            binary_pdf = self.download_pdf(
                                announcementId, title, secName)
                            download_urls.append(
                                "http://www.cninfo.com.cn/new/announcement/download?bulletinId=" + str(announcementId))
                            pdfs.append(binary_pdf)
                        data = {
                            'publisher': secNames,
                            'title': titles,
                            'time': times,
                            'download_url': download_urls
                        }
                        self.dataframe = pd.concat(
                            [self.dataframe, pd.DataFrame(data)])
                        num = num - page_size * \
                            (self.rounds - i + 1) + totalAnnouncement
                    pbar.update(1)
            else:
                print(
                    f"There are no announcements of type {self.announcement_type} reported during the period from " + self.start_date + " to " + self.end_date + ".")
                num = -1
            time.sleep(delay)
        return self.dataframe.to_dict(orient='split')

    def download_pdf(self, announcementId, title, secName):
        url = "http://www.cninfo.com.cn/new/announcement/download"
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
            try:
                binary_pdf = Binary(res.content)
                pdf_document = {
                    "secName": [secName],
                    "title": [title],
                    "file": [binary_pdf]
                }
                self.db_connection.save_data(self.public_announcement_type, self.source, pd.DataFrame(
                    pdf_document).to_dict(orient='split'))
                print(f'{title} has been saved to MongoDB')
            except Exception as e:
                print(f'Save to MongoDB failed: {e}')
                binary_pdf = None
        except Exception as e:
            print(f'Download failed: {e}')
            binary_pdf = None
        return binary_pdf


if __name__ == "__main__":
    from config import config
    c = Juchao_Public_Announcement(config)
    print(c.download())

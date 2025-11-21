import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    仅对 A 股上市公司有效。
    获取新浪财经指定公司的公告。
    注意: 该网站并不是所有公司都有公告。
'''
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from tqdm import tqdm
from data_connection.mongodb import MongoConnection
from lxml import etree
import time


class Sina_Specific_Company_Random_Announcement(Usable_IP):
    def __init__(self, ticker):
        self.ticker = ticker
        self.headers = {
            "User-Agent": UserAgent().random,
            'Accept-Encoding': 'gzip, deflate, br',
            'authority': 'vip.stock.finance.sina.com.cn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
        self.db_connection = MongoConnection('Announcement')
        self.source = "sina"
        self.rounds = 1

    def download(self):
        print(f"Getting page for {self.ticker}:", end=" ")
        page = 0
        while page < self.rounds:
            print("page:", page, end=" ")
            url = f"https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletin.php?stockid={self.ticker}&Page={page}"
            response = self._request_get(url=url, headers=self.headers)
            if response.status_code != 200:
                break
            html = etree.HTML(response.text)  # type: ignore
            # get announcement date
            date_list = html.xpath(
                "/html/body/div[6]/div[2]/div[2]/table[2]/tr/td[2]/div[1]/ul/text()")
            if len(date_list) <= 0:
                break
            date_list = [date.strip('.\r').strip('.\n').strip(
                '.\xa0').strip(' ') for date in date_list]
            date_list = [date for date in date_list if len(date) == 10]
            # get headlines and urls
            url_root = "https://vip.stock.finance.sina.com.cn"
            a_list = html.xpath(
                "/html/body/div[6]/div[2]/div[2]/table[2]/tr/td[2]/div[1]/ul/a")
            headline_list = [a.xpath("./text()")[0] for a in a_list]
            url_list = [url_root + a.xpath("./@href")[0] for a in a_list]
            tmp_df = {
                "date": date_list,
                "headline": headline_list,
                "url": url_list,
            }
            df = pd.DataFrame(tmp_df)
            if not df.empty:
                with tqdm(total=df.shape[0], desc="Getting announcement content") as pbar:
                    df["content"] = df["url"].apply(
                        lambda url: self.get_content(url, pbar))
                df = df.reset_index(drop=True)
                self.db_connection.save_data(
                    self.ticker, self.source, df.to_dict(orient='split'))
            page += 1
        return df

    def get_content(self, url, pbar, delay=0.1):
        time.sleep(delay)
        response = self._request_get(url=url, headers=self.headers)
        if response.status_code == 200:
            try:
                text = response.content.decode('GBK')
                html = etree.HTML(text)  # type: ignore
                # clean content
                content_list = html.xpath("//*[@id='content']//text()")
                content_list = [content.strip('.\t').strip(
                    '.\n').strip('.\r') for content in content_list]
                content_list = [
                    content for content in content_list if len(content) != 0]
                content = "".join(content_list)
            except Exception as e:
                return f"Error, can't get content: {e}"
        else:
            return "Error, can't get content."
        pbar.update(1)
        return content


if __name__ == "__main__":
    c = Sina_Specific_Company_Random_Announcement('600519')
    print(c.download())

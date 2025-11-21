import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从谷歌金融获取当天市场动态信息(包括所有证券市场): https://www.google.com/finance/markets/indexes
    参考: https://serpapi.com/blog/scrape-google-finance-markets-in-python/
    有点问题，可能是目标网站结构变了。
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from parsel import Selector
from crawler.datetime_utils import yyyymmdd
import pandas as pd
import re
import requests

class GoogleFinance_Market_Dynamics(Usable_IP):
    def __init__(self, types, timeframe, args={}):
        super().__init__(args)
        self.db_connection = MongoConnection('Market_Information')
        self.types = types
        self.timeframe = timeframe
        self.source = "googlefinance"
        self.base_url = "https://www.google.com/finance/markets/"
        self.headers = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"116.0.5845.111"',
            'sec-ch-ua-full-version-list': '"Chromium";v="116.0.5845.111", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'service-worker-navigation-preload': 'true',
            'upgrade-insecure-requests': '1',
            "User-Agent": UserAgent().random
        }

    def download(self):
        all_data = {}
        for category in self.types:
            if category != 'most-followed':
                if category == 'gainers' or category == 'losers':
                    if self.timeframe == 'now':
                        print(self.base_url+category)
                        html = requests.get(
                            self.base_url+category, headers=self.headers)
                        if html:
                            parsed_data = self.parser(html=html)
                            all_data[category] = parsed_data.to_dict(orient='records')
                    else:
                        continue
                try:
                    html = requests.get(
                        self.base_url+category, headers=self.headers)
                    if html:
                        parsed_data = self.parser(html=html)
                        all_data[category] = parsed_data.to_dict(orient='records')
                except:
                    continue
            else:
                html = requests.get(
                    "https://www.google.com/finance/", headers=self.headers)
                if html:
                    parsed_data = self.parser_most_followed_on_google(
                        html=html)
                    all_data['most-followed'] = parsed_data.to_dict(
                        orient='split')

        # 保存全部数据到数据库
        self.db_connection.save_data(f"{self.types}_{yyyymmdd()}", self.source, all_data)
        
        # 只返回前十个样本
        return_data = {}
        for category, data in all_data.items():
            return_data[category] = data[:10]
        
        return return_data

    def parser(self, html):
        data = {}
        selector = Selector(text=html.text)
        positions = []
        titles = []
        quotes = []
        price_changes = []
        percent_price_changes = []
        for index, stock_results in enumerate(selector.css("li a"), start=1):
            current_percent_change_raw_value = stock_results.css(
                "[jsname=Fe7oBc]::attr(aria-label)").get()
            current_percent_change = re.search(r"\d+\.\d+%", stock_results.css(
                "[jsname=Fe7oBc]::attr(aria-label)").get()).group()  # type: ignore
            # ./quote/SNAP:NASDAQ -> SNAP:NASDAQ
            positions.append(index)
            titles.append(stock_results.css(".ZvmM7::text").get())
            quotes.append(stock_results.css(".COaKTb::text").get())
            price_changes.append(stock_results.css(
                ".SEGxAb .P2Luy::text").get())
            percent_price_changes.append(
                f"+{current_percent_change}" if "Up" in current_percent_change_raw_value else f"-{current_percent_change}")
        data = {
            "position": positions,
            "title": titles,
            "quote": quotes,
            "price_change": price_changes,
            "percent_price_change": percent_price_changes
        }
        return pd.DataFrame(data)

    def parser_most_followed_on_google(self, html):
        selector = Selector(text=html.text)
        titles = []
        quotes = []
        followings = []
        percent_price_changes = []
        for google_most_followed in selector.css(".NaLFgc"):
            current_percent_change_raw_value = google_most_followed.css(
                "[jsname=Fe7oBc]::attr(aria-label)").get()
            try:
                current_percent_change = re.search(r"by\s?(\d+\.\d+)%", google_most_followed.css(
                    "[jsname=Fe7oBc]::attr(aria-label)").get()).group(1)  # type: ignore
            except AttributeError:
                return "Failed to crawl content."
            try:
                titles.append(google_most_followed.css(".TwnKPb::text").get())
                quotes.append(re.search(r"\.\/quote\/(\w+):",
                              google_most_followed.attrib["href"]).group(1))
                followings.append(re.search(
                    r"(\d+\.\d+)M", google_most_followed.css(".Iap8Fc::text").get()).group(1)) # type: ignore
                percent_price_changes.append(
                    f"+{current_percent_change}" if "Up" in current_percent_change_raw_value else f"-{current_percent_change}")
            except AttributeError:
                return "Failed to crawl content."
        data = {
            "title": titles,
            "quote": quotes,
            "following": followings,
            "percent_price_change": percent_price_changes
        }
        return pd.DataFrame(data)


if __name__ == "__main__":
    types = ["gainers", "losers", "indexes"]
    timeframe = 'now'
    c = GoogleFinance_Market_Dynamics(types=types, timeframe=timeframe)
    data = c.download()
    print(data)

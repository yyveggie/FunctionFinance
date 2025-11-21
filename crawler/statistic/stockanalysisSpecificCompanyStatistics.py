import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的各类统计数据的大致信息，包括总估值、重要的日子、发行股票统计、估值比率、企业估值、财务状况、
    财务效率、税收、股价统计、卖空信息、利润表、资产负债表、现金流量、利率、股息和收益率、分析师预测、股票分割、分数。
    可以划分为基本面数据和市场数据。
'''
import requests
import json
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree


class StockAnalysis_Specific_Company_Statistic(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Statistic')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"1ov6wil"',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    def download(self):
        try:
            url = 'https://stockanalysis.com/api/symbol/s/' + self.ticker + '/statistics'
            response = requests.get(url=url, headers=self.headers)
            statistics = json.loads(response.text)["data"]
        except:
            url = "https://stockanalysis.com/stocks/" + self.ticker + "/statistics/"
            response = requests.get(url=url, headers=self.headers)
            text = response.text
            html = etree.HTML(text, parser=None)
            statistics = {}
            div_count_1 = html.xpath(
                'count(//*[@id="main"]/div[2]/div[1]/div)')
            for i in range(int(div_count_1)):
                title = html.xpath(
                    '//*[@id="main"]/div[2]/div[1]/div[' + str(i+1) + ']/h2/text()')
                words = html.xpath(
                    '//*[@id="main"]/div[2]/div[1]/div[' + str(i+1) + ']/p/text()')
                table_with_space = html.xpath(
                    '//*[@id="main"]/div[2]/div[1]/div[' + str(i+1) + ']/table//text()')
                table = self.create_dict_from_spaced_list(table_with_space)
                try:
                    statistics[title[0]] = [words[0], table]
                except IndexError:
                    statistics[title[0]] = [words, table]
            div_count_2 = html.xpath(
                'count(//*[@id="main"]/div[2]/div[2]/div)')
            for i in range(int(div_count_2)):
                title = html.xpath(
                    '//*[@id="main"]/div[2]/div[2]/div[' + str(i+1) + ']/h2/text()')
                words = html.xpath(
                    '//*[@id="main"]/div[2]/div[2]/div[' + str(i+1) + ']/p/text()')
                table_with_space = html.xpath(
                    '//*[@id="main"]/div[2]/div[2]/div[' + str(i+1) + ']/table//text()')
                table = self.create_dict_from_spaced_list(table_with_space)
                try:
                    statistics[title[0]] = [words[0], table]
                except IndexError:
                    statistics[title[0]] = [words, table]
            div_count_3 = html.xpath(
                'count(//*[@id="main"]/div[2]/div[3]/div)')
            for i in range(int(div_count_3)):
                title = html.xpath(
                    '//*[@id="main"]/div[2]/div[3]/div[' + str(i+1) + ']/h2/text()')
                words = html.xpath(
                    '//*[@id="main"]/div[2]/div[3]/div[' + str(i+1) + ']/p/text()')
                table_with_space = html.xpath(
                    '//*[@id="main"]/div[2]/div[3]/div[' + str(i+1) + ']/table//text()')
                table = self.create_dict_from_spaced_list(table_with_space)
                try:
                    statistics[title[0]] = [words[0], table]
                except IndexError:
                    statistics[title[0]] = [words, table]
        data_dict = dict_to_split_dict(statistics)
        self.db_connection.save_data(self.ticker, self.source, data_dict)
        return data_dict

    def create_dict_from_spaced_list(self, input_list):
        result_dict = {}
        key, value = None, None
        for item in input_list:
            if item.strip():
                if key is None:
                    key = item
                elif value is None:
                    value = item
                    result_dict[key] = value
                    key, value = None, None
        return result_dict


if __name__ == "__main__":
    c = StockAnalysis_Specific_Company_Statistic("AAPL")
    print(c.download())

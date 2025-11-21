import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的公司的概述和雇员情况。
'''
import requests
import re
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree


class StockAnalysis_Specific_Company_Profile(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Profile')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"15z1wvg"',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
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
        url = 'https://stockanalysis.com/stocks/' + self.ticker + '/company/'
        text = self.request_get_sync(url=url, headers=self.headers)
        html = etree.HTML(text, parser=None)
        # 基础信息
        basicInformation = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[1]/table//text()')
        basicInformation = self.list_to_dict(basicInformation)
        # 公司介绍
        companyDescription = html.xpath(
            '//*[@id="main"]/div[2]/div[1]//text()')
        companyDescription = self.list_to_dict(companyDescription)
        # 主要管理人员
        keyExecutives_name = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[1]/tbody/tr/td[1]/text()')
        keyExecutives_position = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[1]/tbody/tr/td[2]/text()')
        keyExecutives = self.lists_to_dict(
            keyExecutives_name, keyExecutives_position)
        # 联系方式
        contactDetails = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[2]/table//text()')
        contactDetails = self.list_to_dict(contactDetails)
        # 股票细节
        stockDetails = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[3]/table//text()')
        stockDetails = self.list_to_dict(stockDetails)
        # 最新的美国证券交易委员会文件
        latestSECFilings_date = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[2]/tbody/tr/td[1]/text()')
        latestSECFilings_type = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[2]/tbody/tr/td[2]/text()')
        latestSECFilings_title = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[2]/tbody/tr/td[3]//text()')
        latestSECFilings_url = html.xpath(
            '//*[@id="main"]/div[2]/div[3]/table[2]/tbody/tr/td[3]/a/@href')
        latestSECFilings = {"date": latestSECFilings_date, "type": latestSECFilings_type,
                            "title": latestSECFilings_title, "url": latestSECFilings_url}
        # 雇员情况
        employee = self.download_employees()
        dict_list = [
            basicInformation, companyDescription, keyExecutives, contactDetails, stockDetails, latestSECFilings, employee
        ]
        keys = [
            "basicInformation", "companyDescription", "keyExecutives", "contactDetails", "stockDetails", "latestSECFilings", "employee"
        ]
        profile = {key: dict_list[i] for i, key in enumerate(keys)}
        data_dict = dict_to_split_dict(profile)
        self.db_connection.save_data(self.ticker, self.source, data_dict)
        return data_dict

    def download_employees(self):
        url = 'https://stockanalysis.com/stocks/' + self.ticker + '/employees/'
        response = requests.get(url=url, headers=self.headers)
        text = response.text
        html = etree.HTML(text, parser=None)
        try:
            summarize = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[1]/div/div/div[2]/p/text()')
        except:
            summarize = None
        script_text = self.find_last_script(text)
        stats_match = re.search(
            r'stats:\{(.*?)\},historical', script_text, re.DOTALL)  # type: ignore
        stats_str = '{' + stats_match.group(1) + '}'
        stats_str = re.sub(r'(\w+):', r'"\1":', stats_str)
        stats_str = stats_str.replace('null', 'None').replace(
            'true', 'True').replace('false', 'False')
        stats = eval(stats_str)
        historical_match = re.search(
            r'historical:\[(.*?)\],news', script_text, re.DOTALL)  # type: ignore
        historical_str = '[' + historical_match.group(1) + ']'
        historical_str = re.sub(r'(\w+):', r'"\1":', historical_str)
        historical_str = historical_str.replace('null', 'None').replace(
            'true', 'True').replace('false', 'False')
        historical = eval(historical_str)
        employeesTrending = {"stats": stats, "historical": historical}
        employees = {"summarize": summarize,
                     "employeesTrending": employeesTrending}
        return employees

    def list_to_dict(self, lst):
        result = {}
        key = None
        value = ""
        for item in lst:
            if item not in ['', ' ']:
                if key is None:
                    key = item
                else:
                    if value:
                        value += " "
                    value += item
            else:
                if key is not None and value:
                    result[key] = value.strip()
                    key = None
                    value = ""
        if key is not None and value:
            result[key] = value.strip()
        return result

    def lists_to_dict(self, keys_list, values_list):
        return dict(zip(keys_list, values_list))  # type: ignore

    def find_last_script(self, html_content):
        end_script_index = html_content.rfind('</script>')
        if end_script_index == -1:
            return None
        start_script_index = html_content.rfind(
            '<script>', 0, end_script_index)
        if start_script_index == -1:
            return None
        # +8 跳过 "<script>"
        script_content = html_content[start_script_index +
                                      8:end_script_index].strip()
        return script_content


if __name__ == "__main__":
    from config import config
    c = StockAnalysis_Specific_Company_Profile(ticker='BABA', args=config)
    print(c.download())

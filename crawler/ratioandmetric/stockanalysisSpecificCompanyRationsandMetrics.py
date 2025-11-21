import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的年度各种比率和衡量指标。
'''
from crawler.utils import dict_to_split_dict, remove_unwanted_values
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from lxml import etree


class StockAnalysis_Specific_Company_Ration_and_Metric(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = MongoConnection('Ratios_and_Metrics')
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
        url = "https://stockanalysis.com/stocks/" + self.ticker + "/financials/ratios/"
        text = self.request_get_sync(url=url, headers=self.headers)
        html = etree.HTML(text, parser=None)
        year_raw = html.xpath('//*[@id="main"]//table/thead/tr//text()')
        year = self.list_to_dict_with_non_empty_values(year_raw)
        tr_count = html.xpath('count(//*[@id="main"]//table/tbody/tr)')
        ratios_and_metrics_list = []
        for i in range(int(tr_count)):
            value_raw = html.xpath(
                '//*[@id="main"]//table/tbody/tr[' + str(i+1) + ']//text()')
            value = self.list_to_dict_with_non_empty_values(value_raw)
            ratios_and_metrics_list.append(value)
        remark = html.xpath(
            '//*[@id="main"]/div[3]/div[1]/div[2]/div[1]/text()')[0]
        ratios_and_metrics_df = self.adjust_index_and_create_dataframe(
            ratios_and_metrics_list, year)
        ratios_and_metrics = {
            "remark": remark,
            "ratios_and_metrics": ratios_and_metrics_df.to_dict(orient='split')
        }
        data_dict = remove_unwanted_values(
            dict_to_split_dict(ratios_and_metrics))
        self.db_connection.save_data(self.ticker, self.source, data_dict)
        return data_dict

    def list_to_dict_with_non_empty_values(self, input_list):
        for item in input_list:
            if item.strip():
                key = item
                break
        start_index = input_list.index(key) + 1
        values = [item for item in input_list[start_index:] if item.strip()]
        result_dict = {key: values}
        return result_dict

    def adjust_index_and_create_dataframe(self, data, index_dict):
        df = pd.DataFrame()
        for item in data:
            item_df = pd.DataFrame(item)
            df = pd.concat([df, item_df], axis=1)
        index_col = list(index_dict.keys())[0]
        index_values = index_dict[index_col]
        while len(df) < len(index_values):
            df.loc[len(df)] = [None] * len(df.columns)
        df.index = index_values
        if "Quarters" in str(df.index[-1]):
            df = df.drop(df.index[-1])
        return df


if __name__ == "__main__":
    c = StockAnalysis_Specific_Company_Ration_and_Metric("AAPL")
    print(c.download())

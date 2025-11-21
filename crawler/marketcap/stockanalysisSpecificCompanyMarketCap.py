import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的市值变化。
'''
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from lxml import etree
import json
import asyncio

class StockAnalysis_Specific_Company_MarketCap(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Market_Cap')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
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

    async def download_recent_marketcap(self):
        try:
            url_recent = "https://stockanalysis.com/api/symbol/s/" + self.ticker + "/marketcap"
            response_recent = await self.request_get(
                url=url_recent, headers=self.headers)
            marketCap = {
                "marketCap":dict_to_split_dict(json.loads(response_recent)["data"]),
            }
        except:
            marketCap = {}
            url_summary = "https://stockanalysis.com/stocks/" + self.ticker + "/market-cap/"
            response_summary = await self.request_get(
                url=url_summary, headers=self.headers)
            try:
                html = etree.HTML(response_summary.text)  # type: ignore
            except Exception as e:
                return f'Ticker {self.ticker} does not exist in stockanalysis.com'
            summary = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[1]/div/div[2]/p/text()')
            table_raw = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[2]//text()')
            table = dict_to_split_dict(
                self.create_dict_from_list_with_space_delimiter(table_raw))
            marketCap["summary"] = dict_to_split_dict(summary)[0]
            marketCap["table"] = dict_to_split_dict(table)
            recent_history = self.download_recent_history(html)
            marketCap["recent_data"] = recent_history.to_dict(orient='split')
        marketCap = dict_to_split_dict(marketCap)
        await self.db_connection.save_data(self.ticker, self.source, marketCap)
        return marketCap

    async def download_all_marketcap(self):
        try:
            url_recent = "https://stockanalysis.com/api/symbol/s/" + self.ticker + "/marketcap"
            response_recent = await self.request_get(
                url=url_recent, headers=self.headers)
            url_history = "https://stockanalysis.com/api/symbol/s/" + \
                self.ticker + "/marketcap?t=price"
            response_history = await self.request_get(
                url=url_history, headers=self.headers)
            marketCap = {
                "marketCap": dict_to_split_dict(json.loads(response_recent)["data"]),
                "history": dict_to_split_dict(json.loads(response_history)["data"])
            }
        except:
            marketCap = {}
            url_summary = "https://stockanalysis.com/stocks/" + self.ticker + "/market-cap/"
            response_summary = await self.request_get(
                url=url_summary, headers=self.headers)
            try:
                html = etree.HTML(response_summary.text)  # type: ignore
            except Exception as e:
                return f'Ticker {self.ticker} does not exist in stockanalysis.com'
            summary = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[1]/div/div[2]/p/text()')
            table_raw = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[2]//text()')
            table = dict_to_split_dict(
                self.create_dict_from_list_with_space_delimiter(table_raw))
            marketCap["summary"] = dict_to_split_dict(summary)[0]
            marketCap["table"] = dict_to_split_dict(table)
            marketCapChartSummary = html.xpath(
                '//*[@id="main"]/div[2]/div[1]/div[3]/div[3]/div/div[2]/p/text()')[0]
            history_data = self.download_history(self.ticker)
            marketCap["history"] = dict_to_split_dict(
                {"marketCapChartSummary": marketCapChartSummary, "history_data": history_data})
            recent_history = self.download_recent_history(html)
            marketCap["history_data"] = recent_history.to_dict(orient='split')
        marketCap = dict_to_split_dict(marketCap)
        await self.db_connection.save_data(self.ticker, self.source, marketCap)
        return marketCap

    async def download_history(self, ticker):
        url = "https://stockanalysis.com/api/symbol/s/" + ticker + "/marketcap?t=price"
        response = self.request_get(url=url, headers=self.headers)
        data = json.loads(response)["data"]
        return data

    async def download_recent_history(self, html):
        marketCapHistory_raw = html.xpath(
            '//*[@id="main"]/div[2]/div[1]/div[4]/div[1]/div[2]/table//text()')
        marketCapHistory = await self.create_dataframe_from_list(
            marketCapHistory_raw)
        return marketCapHistory

    async def create_dict_from_list_with_space_delimiter(self, input_list):
        result_dict = {}
        key, value_parts = None, []
        for item in input_list:
            cleaned_item = item.strip().replace('\n', '').replace('\t', '')
            if cleaned_item:
                if key is None:
                    key = cleaned_item
                else:
                    value_parts.append(cleaned_item)
            else:
                if key is not None:
                    result_dict[key] = ' '.join(value_parts)
                    key, value_parts = None, []
        if key is not None:
            result_dict[key] = ' '.join(value_parts)
        return result_dict

    async def create_dataframe_from_list(self, data_list):
        column_count = data_list.index(' ')
        column_names = data_list[:column_count]
        data_without_spaces = [
            x for x in data_list[column_count+1:] if x != ' ']
        rows = [data_without_spaces[i:i+column_count]
                for i in range(0, len(data_without_spaces), column_count)]
        return pd.DataFrame(rows, columns=column_names)

    
async def main(ticker):
    c = StockAnalysis_Specific_Company_MarketCap(ticker)
    return await c.download_recent_marketcap()

if __name__ == "__main__":
    print(asyncio.run(main('BABA')))

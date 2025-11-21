import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的表现概述, 包括最新的市值、收入、净利润什么的, 以及购买建议等。
'''
import re
import json
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from lxml import etree


class StockAnalysis_Specific_Company_Overview(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Overview')
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

    async def download(self):
        url = 'https://stockanalysis.com/stocks/' + self.ticker
        text = await self.request_get(url=url, headers=self.headers)
        html = etree.HTML(text)  # type: ignore
        overview = await self.download_overview(html)
        financial_performance = await self.download_financialPerformance(text)
        analyst_forecast = await self.download_analystForecast(text)
        data = {
            "overview": overview,
            "financial_performance": financial_performance,
            "analyst_forecast": analyst_forecast
        }
        await self.db_connection.save_data(self.ticker, self.source, data)
        return data

    async def download_overview(self, html):
        overview_list = html.xpath('//*[@id="main"]/div[2]/div[2]//text()')
        overview = {}
        key = None
        for item in overview_list:
            if item.strip():
                if key is None:
                    key = item
                else:
                    overview[key] = item
                    key = None
        return overview

    async def download_financialPerformance(self, text):
        financialIntro = re.search(
            r'financialIntro:"(.*?)",financialChart', text, re.DOTALL).group(1)
        financialChart = re.search(
            r'financialChart:(.*?),analystIntro', text, re.DOTALL).group(1)
        financialChart = await self.turn_to_json(financialChart)
        financialPerformance = {
            "financialIntro": financialIntro, "financialChart": financialChart
        }
        return financialPerformance

    async def download_analystForecast(self, text):
        analystIntro = re.search(
            r'analystIntro:"(.*?)",analystTarget', text, re.DOTALL).group(1)  # type: ignore
        analystTarget = re.search(
            r'analystTarget:(.*?),analystChart', text, re.DOTALL).group(1)
        analystChart = re.search(
            r'analystChart:(.*?),news:', text, re.DOTALL).group(1)
        analystForecast = {
            "analystIntro": analystIntro, "analystTarget": analystTarget, "analystChart": analystChart
        }
        return analystForecast

    async def turn_to_json(self, str):
        formatted_str = re.sub(r'(\b\w+\b):', r'"\1":', str)
        try:
            data_json = json.loads(formatted_str)
        except json.JSONDecodeError as e:
            data_json = str
            print("Parse error:", e)
        return data_json


async def main(ticker):
    c = StockAnalysis_Specific_Company_Overview(ticker)
    return await c.download()

if __name__ == "__main__":
    data = asyncio.run(main('aapl'))
    print(data)
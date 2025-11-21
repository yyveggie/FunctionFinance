import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定时间点的企业行动，包括企业行动概览，上市的股票，退市的股票，分拆的股票，代码变更的股票，
    分割的股票，破产的股票，兼并和收购。
    不能指定企业。
    每年更新一次。
    https://stockanalysis.com/actions/
'''
import aiohttp
import asyncio
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime
from lxml import etree
import pandas as pd


class StockAnalysis_Specific_Year_Public_Corporate_Actions(Usable_IP):
    def __init__(self, year, type, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.year = year
        self.type = type
        self.current_year = datetime.now().year
        self.db_connection = AsyncMongoConnection('Corporate_Actions')
        self.source = 'stockanalysis.com'
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

    async def _download_data(self):
        url = f"https://stockanalysis.com/actions/{self.type}/{self.year}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    html = await response.text()
                    html = etree.HTML(html, parser=None)
                    columns = html.xpath(
                        '//*[@id="main"]/div[2]/div/div/div[2]/table/thead//text()')
                    columns = [item.strip() for item in columns if item not in [
                        None, ""] and not str(item).isspace()]
                    rows = []
                    tr_count = html.xpath(
                        'count(//*[@id="main"]/div[2]/div/div/div[2]/table/tbody/tr)')
                    for i in range(int(tr_count)):
                        row = html.xpath(
                            f'//*[@id="main"]/div[2]/div/div/div[2]/table/tbody/tr[{i+1}]//text()')
                        rows.append([item.strip() for item in row if item not in [
                                    None, ""] and not str(item).isspace()])
                    df = pd.DataFrame(rows, columns=columns)
                    await self.db_connection.save_data(self.type, self.source, df.to_dict(orient='records'))
                    return df
            except Exception as e:
                return f'Error: {e}'

if __name__ == "__main__":
    c = StockAnalysis_Specific_Year_Public_Corporate_Actions('2023', 'delisted')
    print(asyncio.run(c._download_data()))
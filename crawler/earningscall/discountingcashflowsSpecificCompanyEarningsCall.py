import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 discountingcashflows.com 下载指定公司指定时间的财报电话会议。
'''
import re
import json
import asyncio
from typing import List
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from datetime import datetime


class Discountingcashflows_Specific_Company_Earnings_Call(Usable_IP):
    def __init__(self, ticker, year, quarter, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        assert self.quarter in [
            "Q1", "Q2", "Q3", "Q4"], 'The quarter should from the list ["Q1","Q2","Q3","Q4"]'
        self.db_connection = AsyncMongoConnection('EarningCall')
        self.source = "discountingcashflows.com"

    async def download(self):
        resp_dict, speakers_list = await self.get_earnings_transcripts()
        data = {
            "text": resp_dict["content"],
            "date": resp_dict["date"],
            "year_and_quarter": self.year + ' ' + self.quarter,
            "speakers_list": speakers_list,
        }
        await self.db_connection.save_data(self.ticker, self.source, data)
        return data

    async def correct_date(self, yr, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        if dt.year != yr:
            dt = dt.replace(year=yr)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    async def extract_speakers(self, cont: str) -> List[str]:
        pattern = re.compile(r"\n(.*?):")
        matches = pattern.findall(cont)
        return list(set(matches))

    async def get_earnings_transcripts(self):
        headers = {
            'user-agent': UserAgent().random
        }
        text = await self.request_get(
            f"https://discountingcashflows.com/api/transcript/{self.ticker}/{self.quarter}/{self.year}/",
            headers=headers,
            # auth=("user", "pass")
        )
        try:
            resp_text = json.loads(text)
            speakers_list = await self.extract_speakers(resp_text[0]["content"])
            corrected_date = await self.correct_date(
                resp_text[0]["year"], resp_text[0]["date"])
            resp_text[0]["date"] = corrected_date
            return resp_text[0], speakers_list
        except:
            return None, None

async def main(ticker, year, quarter):
    c = Discountingcashflows_Specific_Company_Earnings_Call(
        ticker=ticker, year=year, quarter=quarter)
    result = await c.download()
    return result

if __name__ == "__main__":
    ticker = 'AAPL'
    year = '2023'
    quarter = 'Q4'
    print(asyncio.run(main(ticker, year, quarter)))

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的利润表。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree
import asyncio


class StockAnalysis_Specific_Company_Income_Statement(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Income_Statement')
        self.source = "stockanalysis"
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

    async def download(self):
        url = "https://stockanalysis.com/stocks/" + self.ticker + "/financials/"
        response = await self.request_get(url=url, headers=self.headers)
        html = etree.HTML(response, parser=None)
        year_raw = html.xpath('//*[@id="main"]//table/thead/tr//text()')
        year = await self.list_to_dict_with_non_empty_values(year_raw)
        tr_count = html.xpath('count(//*[@id="main"]//table/tbody/tr)')
        income_statement_dict = {}
        for i in range(int(tr_count)):
            key_raw = html.xpath(
                '//*[@id="main"]//table/tbody/tr[' + str(i+1) + ']/td[1]//text()')
            key = ''.join(key_raw).strip()
            value_raw = html.xpath(
                '//*[@id="main"]//table/tbody/tr[' + str(i+1) + ']/td[position()>1]//text()')
            value = [item.strip() for item in value_raw if item.strip()]
            income_statement_dict[key] = dict(zip(year[list(year.keys())[0]], value))
        remark = html.xpath(
            '//*[@id="main"]/div[3]/div[1]/div[2]/div[1]/text()')[0]
        income_statement = {
            "remark": remark,
            "income statement": income_statement_dict
        }
        await self.db_connection.save_data(self.ticker, self.source, income_statement)
        return await self.remove_unwanted_values(income_statement)

    async def list_to_dict_with_non_empty_values(self, input_list):
        for item in input_list:
            if item.strip():
                key = item
                break
        start_index = input_list.index(key) + 1
        values = [item for item in input_list[start_index:] if item.strip()]
        result_dict = {key: values}
        return result_dict

    async def remove_unwanted_values(self, data, unwanted_value='Upgrade\n\t\t'):
        if isinstance(data, dict):
            return {k: await self.remove_unwanted_values(v, unwanted_value) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self.remove_unwanted_values(item, unwanted_value) for item in data if item != unwanted_value]
        else:
            return data


async def main(ticker):
    c = StockAnalysis_Specific_Company_Income_Statement(ticker=ticker)
    return await c.download()

if __name__ == "__main__":
    data = asyncio.run(main('AAPL'))
    print(data)
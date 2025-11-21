import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的年度现金流量表。
'''
import asyncio
from crawler.utils import remove_unwanted_values
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree

class StockAnalysis_Specific_Company_Cash_Flow_Statement(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Cash_Flow_Statement')
        self.source = 'stockanalysis.com'

    async def download(self):
        headers = {
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
        url = "https://stockanalysis.com/stocks/" + self.ticker + "/financials/cash-flow-statement/"
        try:
            text = await self.request_get(url=url, headers=headers)
            html = etree.HTML(text, parser=None)
        except Exception as e:
            return f"Request error: {e}"

        year_raw = html.xpath('//*[@id="main"]//table/thead/tr//text()')
        year = await self.list_to_dict_with_non_empty_values(year_raw)

        tr_count = html.xpath('count(//*[@id="main"]//table/tbody/tr)')
        cash_flow_statement_list = []
        for i in range(int(tr_count)):
            value_raw = html.xpath('//*[@id="main"]//table/tbody/tr[' + str(i+1) + ']//text()')
            value = await self.list_to_dict_with_non_empty_values(value_raw)
            cash_flow_statement_list.append(value)

        remark = html.xpath('//*[@id="main"]/div[3]/div[1]/div[2]/div[1]/text()')[0]

        # 创建嵌套字典
        output_dict = {}
        for i in range(len(year[list(year.keys())[0]])):
            year_key = year[list(year.keys())[0]][i]
            output_dict[year_key] = {"remark": remark}
            for j in range(len(cash_flow_statement_list)):
                key = list(cash_flow_statement_list[j].keys())[0]
                value = cash_flow_statement_list[j][key][i]
                output_dict[year_key][key] = value

        await self.db_connection.save_data(self.ticker, self.source, output_dict)
        return remove_unwanted_values(output_dict)

    async def list_to_dict_with_non_empty_values(self, input_list):
        for item in input_list:
            if item.strip():
                key = item
                break
        start_index = input_list.index(key) + 1
        values = [item for item in input_list[start_index:] if item.strip()]
        result_dict = {key: values}
        return result_dict

async def main(ticker):
    c = StockAnalysis_Specific_Company_Cash_Flow_Statement(ticker)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('AAPL')))
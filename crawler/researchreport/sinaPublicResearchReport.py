import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从新浪财经下载市场上的研究报告, 但无法指定公司。
    无法指定类型, 但可以选择指定日期的研报。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
import pandas as pd
from lxml import etree
import asyncio

class Sina_Public_ResearchReport(Usable_IP):
    def __init__(self, date, args={}):
        super().__init__(args)
        self.specific_date = date
        self.db_connection = AsyncMongoConnection('Research_Report')
        self.dataframe = pd.DataFrame()
        self.source = "sina.com"
        self.rounds = 2
        self.headers = {
            'authority': 'stock.finance.sina.com.cn',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            "referer": "https://stock.finance.sina.com.cn/stock",
            "user-agent": UserAgent().random
        }

    async def download(self):
        base_url = "https://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/search/index.phtml"
        for i in range(self.rounds):
            params = {
                "t1": 6,
                "pubdate": self.specific_date,
                "p": i+1,
            }
            text = await self.request_get(
                base_url, headers=self.headers, params=params)
            try:
                html = etree.HTML(text, parser=None)
            except Exception as e:
                return f'Parse error: {e}'
            titles = html.xpath(
                "//div[@class='main']//td[@class='tal f14']/a/text()")
            titles = [title.strip() for title in titles]
            urls = html.xpath(
                "//div[@class='main']//td[@class='tal f14']/a/@href")
            types = html.xpath(
                '//div[@class="main"]//table[@class="tb_01"]//tr//td[3]/text()')
            organizations = html.xpath(
                '//div[@class="main"]//table[@class="tb_01"]//tr//div[@class="fname05"]//text()')
            researchers = html.xpath(
                '//div[@class="main"]//table[@class="tb_01"]//tr//div[@class="fname"]//text()')
            # download contents
            contents = []
            for url in urls:
                headers_content = {
                    "referer": base_url + "?" + "t1=6&pubdate=" + self.specific_date + "&p=" + str(i+1),
                    "user-agent": UserAgent().random
                }
                res_content = await self.request_get(
                    url="https:"+url, headers=headers_content)  # type: ignore
                html_content = etree.HTML(res_content, parser=None)
                content = html_content.xpath(
                    "/html/body/div/div[3]/div[1]/div/div/div[2]/p/text()")
                content = ''.join(content).replace('\u3000', '').replace(
                    '\xa0', '').replace('\r\n', ' ')
                contents.append(content)
            data = {
                'published_date': [self.specific_date] * len(titles),
                'title': titles,
                'url': urls,
                "type": types,
                "organization": organizations,
                "researcher": researchers,
                "content": contents
            }
            max_len = max(len(l) for l in data.values())
            for key, value in data.items():
                data[key] = value + [""] * (max_len - len(value))
            self.dataframe = pd.concat([pd.DataFrame(data), self.dataframe])
            data_list = self.dataframe.to_dict(orient='records')
        await self.db_connection.save_data(
            self.specific_date, self.source, data_list)
        return data_list

async def main(date):
    from config import config
    c = Sina_Public_ResearchReport(date=date, args=config)
    return await c.download()

if __name__ == "__main__":
    print(asyncio.run(main('2024-04-29')))
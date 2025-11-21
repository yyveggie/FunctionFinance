import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从谷歌金融下载指定关键词的市场信息。
    来源 serpapi API, 免费用户每月100次访问: https://serpapi.com/dashboard
    这个 JSON 数据提供了一个全面的市场概览, 涵盖了股票、期货、加密货币、货币汇率和市场新闻等多个方面:
        discover_more: 包含了一系列股票和指数的信息，例如 Dow Jones Industrial Average、S&P 500、Tesla Inc、Apple Inc 等。每个条目提供了股票名称、当前价格、价格变动（上涨或下跌及其百分比）、相关链接和股票代码。
        futures_chain: 列出了与指定公司相关的不同市场的期货信息，包括价格、价格变动、链接和股票代码。
        markets: 提供了全球不同市场的概览，包括亚洲、欧洲、美国市场的主要指数，如 Nikkei 225、DAX、FTSE 100、Dow Jones 等，以及它们的当前价格和价格变动情况。
        crypto: 列出了主要加密货币的市场信息，包括比特币、以太坊、瑞波币等的价格和价格变动情况。
        currencies: 提供了主要货币对的汇率信息，如 EUR/USD、GBP/USD、USD/JPY 等。
        top_news: 包含了一条关于股市的最新新闻，提供了新闻标题、链接、来源和发布时间。
        search_metadata 和 search_parameters: 包含了关于搜索的元数据和参数，如搜索创建时间、处理时间、搜索引擎、查询关键词等。

    注意：数据不好处理，暂时搁置。        
'''
import os
import serpapi
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP


class GoogleFinance_Specific_Keyword_Market_Dynamic(Usable_IP):
    def __init__(self, args={}):
        super().__init__(args)
        self.apikey = os.environ.get('Serpapi_KEY')
        # self.keyword
        self.db_connection = MongoConnection('Market_Dynamics')
        self.source = "googlefinance"

    def download(self):
        params = {
            "engine": "google_finance",
            "q": 'hi',
            "api_key": self.apikey,
        }
        # JSON output includes structured data for "Markets", "Graph", "Summary", "Knowledge graph", "News Results", "Financials", "Futures chain" and "Discover More".
        search = dict(serpapi.search(params))
        data = search.pop('discover_more')
        self.db_connection.save_data('public', self.source, search)
        return data


if __name__ == "__main__":
    from config import config
    c = GoogleFinance_Specific_Keyword_Market_Dynamic(config)
    # print(c.download())
    import pprint
    print(pprint.pprint(c.download()))

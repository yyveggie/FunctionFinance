import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import asyncio
from scheduler import historical_data_retrieval, quick_latest_data, web_scrape

class Data_Acquisition:
    def __init__(self, query, latest_news, latest_financial_data, historical_financial_data) -> None:
        self.query = query
        self.latest_news = latest_news
        self.latest_financial_data = latest_financial_data
        self.historical_financial_data = historical_financial_data

    def __call__(self):
        results = []
        if self.latest_news:
            results.append(asyncio.run(web_scrape.run(self.query)))
        elif self.latest_financial_data:
            results.append(quick_latest_data.run(self.query))
        elif self.historical_financial_data:
            results.append(asyncio.run(historical_data_retrieval.run(self.query)))
        return results

def run(query, latest_news, latest_financial_data, historical_financial_data):
    parser = Data_Acquisition(query, latest_news, latest_financial_data, historical_financial_data)
    return parser()

# if __name__ == "__main__":
#     query = input("请问您想搜索什么：")
#     print(run(query))
#         # 我想知道特斯拉的最新市盈率、市净率、股价是多少
#         # "茅台的十大股东是哪些",
#         # "茅台的历史行情数据",
#         # "分析一下今天关于阿里巴巴的新闻",
#         # "谷歌的市盈率是多少？",
#         # "根据特斯拉历史财报进行分析",

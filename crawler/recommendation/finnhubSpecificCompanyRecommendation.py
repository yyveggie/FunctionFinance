'''
每月月初更新一次，对每一支股票的分析家推荐趋势。
'''
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.mongodb import MongoConnection
import finnhub
import os

class Finnhub_Specific_Company_Sentiment():
    def __init__(self, ticker):
        self.ticker = ticker
        self.finnhub_client = finnhub.Client(api_key=os.environ.get('Finnhub_KEY'))
        self.db_connection = MongoConnection('Recommendation')
        self.source = 'finnhub.io'

    def download(self):
        data = self.finnhub_client.recommendation_trends(self.ticker)
        self.db_connection.save_data(self.ticker, self.source, data, ordered=False)
        return data

def main(ticker):
    c = Finnhub_Specific_Company_Sentiment(ticker=ticker)
    return c.download()

if __name__ == "__main__":
    from pprint import pprint
    ticker = 'tsla'
    pprint(main(ticker=ticker))
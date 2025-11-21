import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.mongodb import MongoConnection
import finnhub
import os

class Finnhub_Specific_Company_Sentiment():
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.finnhub_client = finnhub.Client(api_key=os.environ.get('Finnhub_KEY'))
        self.db_connection = MongoConnection('Sentiment')
        self.source = 'finnhub.io'

    def download(self):
        data = self.finnhub_client.stock_insider_sentiment(self.ticker, self.start_date, self.end_date)
        self.db_connection.save_data(self.ticker, self.source, data, ordered=False)
        ## 返回：
        # change 改变: Net buying/selling from all insiders' transactions. 所有内部人士交易的净买入/卖出。
        # month 月。
        # mspr: Monthly share purchase ratio. 每月股票购买比例。
        return data

def main(ticker, start_date, end_date):
    c = Finnhub_Specific_Company_Sentiment(ticker=ticker, start_date=start_date, end_date=end_date)
    return c.download()

if __name__ == "__main__":
    from pprint import pprint
    ticker = 'tsla'
    start_date = '2021-01-01'
    end_date = '2024-05-01'
    pprint(main(ticker=ticker, start_date=start_date, end_date=end_date))
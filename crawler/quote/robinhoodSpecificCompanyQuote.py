import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 Robinhood 获得报价数据，具体见：
    https://pyrh.readthedocs.io/en/latest/stubs/pyrh.Robinhood.html
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from pyrh import Robinhood
import os


class Robinhood_Specific_Company_Quote(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.rh = Robinhood(username=os.environ.get(
            'Robinhood_USERNAME'), password=os.environ.get('Robinhood_PASSWORD'))  # type: ignore
        self.rh.login()
        self.db_connection = MongoConnection('Quote')
        self.source = "robinhood.com"

    def download(self):
        try:
            data = self.rh.quote_data(self.ticker)
        except:
            return f'Ticker {self.ticker} does not exist in robinhood.com'
        self.db_connection.save_data(self.ticker, self.source, data)
        return data


if __name__ == '__main__':
    c = Robinhood_Specific_Company_Quote("BABA")
    print(c.download())

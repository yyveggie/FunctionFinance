'''
根据成交量计算，计算标普100或者标普500的行业交易量集中度。
'''
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

class StockVolumeConcentration:
    def __init__(self, index='sp100'):
        self.index = index
        self.data_file = f"{index}_data.pkl"
        self.ticker_list = []
        self.data = None
        self.volume_data = None
        self.ticker_info = {}
        self.industry_concentration = None
        self.hhi = None

    def get_ticker_list(self):
        if self.index == 'sp100':
            self.ticker_list = pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')[2]['Symbol'].tolist()
        elif self.index == 'sp500':
            self.ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        else:
            raise ValueError("Invalid index. Choose either 'sp100' or 'sp500'.")

    def load_data(self):
        if os.path.exists(self.data_file):
            self.data = pd.read_pickle(self.data_file)
        else:
            self.get_ticker_list()
            end_date = datetime.today()
            start_date = end_date - timedelta(days=30)
            with ThreadPoolExecutor() as executor:
                futures = []
                for ticker in self.ticker_list:
                    future = executor.submit(yf.download, ticker, start=start_date, end=end_date, group_by='ticker')
                    futures.append(future)
                self.data = pd.concat([future.result() for future in as_completed(futures)], keys=self.ticker_list)
            self.data.to_pickle(self.data_file)

    def process_data(self):
        self.volume_data = self.data.stack(level=0)['Volume'].reset_index()
        self.volume_data.columns = ['Date', 'Symbols', 'Volume']

        with ThreadPoolExecutor() as executor:
            futures = []
            for ticker in self.volume_data['Symbols'].unique():
                future = executor.submit(yf.Ticker(ticker).info)
                futures.append((ticker, future))

            for ticker, future in futures:
                info = future.result()
                if 'sector' in info:
                    self.ticker_info[ticker] = info['sector']

        self.volume_data['industry'] = self.volume_data['Symbols'].map(self.ticker_info)
        print(f"总记录数: {len(self.volume_data)}")
        self.volume_data = self.volume_data.dropna(subset=['industry'])
        print(f"有行业信息的记录数: {len(self.volume_data)}")

    def calculate_concentration(self):
        industry_volume = self.volume_data.groupby('industry')['Volume'].sum()
        total_volume = industry_volume.sum()
        self.industry_concentration = (industry_volume / total_volume).to_dict()

    def calculate_hhi(self):
        self.hhi = sum(value ** 2 for value in self.industry_concentration.values())

    def run(self):
        self.load_data()
        self.process_data()
        self.calculate_concentration()
        self.calculate_hhi()
        return self.industry_concentration

if __name__ == '__main__':
    # 使用示例
    concentration = StockVolumeConcentration(index='sp100')  # 可选择 'sp100' 或 'sp500'
    result = concentration.run()
    print(result)
'''
获取个股和市场的换手率。
'''
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

class TurnoverRatio:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data = self._download_data()

    def _download_data(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        ticker = yf.Ticker(self.symbol)
        return ticker.history(start=start_date, end=end_date)

    def calculate_turnover_ratio(self):
        volume = self.data['Volume']
        if 'sharesOutstanding' in yf.Ticker(self.symbol).info:
            shares_outstanding = yf.Ticker(self.symbol).info['sharesOutstanding']
            turnover_ratio = volume / shares_outstanding
        else:
            turnover_ratio = volume / volume.shift(1)
        return self._aggregate_monthly_data(turnover_ratio)

    def _aggregate_monthly_data(self, data):
        monthly_data = {}
        end_date = datetime.now().date()
        for month in range(6):
            month_end = end_date - timedelta(days=month*30)
            month_start = month_end - timedelta(days=30)
            monthly_data[month_end.strftime('%Y-%m')] = round(np.nanmean(data[(data.index.date >= month_start) & (data.index.date <= month_end)]), 4)
        return monthly_data

    def get_results(self):
        return self.calculate_turnover_ratio()

if __name__ == '__main__':
    symbol = 'AAPL'
    turnover_ratio = TurnoverRatio(symbol=symbol)
    results = turnover_ratio.get_results()
    print(results)
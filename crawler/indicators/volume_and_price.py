'''
成交量和价格波动：半年内个股或指数的每月变化率
'''
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class VolumeChangeCalculator:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data = self._download_data()

    def _download_data(self):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        data = yf.download(self.symbol, start=start_date, end=end_date)
        return data

    def calculate_monthly_volume_changes(self):
        monthly_data = self.data.resample('ME').mean()
        monthly_volume_changes = {}
        for i in range(1, len(monthly_data)):
            current_month = monthly_data.index[i]
            previous_month = monthly_data.index[i - 1]
            volume_change = (monthly_data['Volume'][current_month] - monthly_data['Volume'][previous_month]) / monthly_data['Volume'][previous_month]
            monthly_volume_changes[current_month.strftime('%Y-%m')] = round(volume_change, 4)
        return monthly_volume_changes

class PriceChangeCalculator:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data = self._download_data()

    def _download_data(self):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        data = yf.download(self.symbol, start=start_date, end=end_date)
        return data

    def calculate_monthly_price_changes(self):
        monthly_data = self.data.resample('ME').mean()
        monthly_price_changes = {}
        for i in range(1, len(monthly_data)):
            current_month = monthly_data.index[i]
            previous_month = monthly_data.index[i - 1]
            price_change = (monthly_data['Close'][current_month] - monthly_data['Close'][previous_month]) / monthly_data['Close'][previous_month]
            monthly_price_changes[current_month.strftime('%Y-%m')] = round(price_change, 4)
        return monthly_price_changes

if __name__ == '__main__':
    symbol = "AAPL"  # 可以输入个股代码或指数代码

    volume_calculator = VolumeChangeCalculator(symbol)
    monthly_volume_changes = volume_calculator.calculate_monthly_volume_changes()
    print(monthly_volume_changes)

    price_calculator = PriceChangeCalculator(symbol)
    monthly_price_changes = price_calculator.calculate_monthly_price_changes()
    print(monthly_price_changes)

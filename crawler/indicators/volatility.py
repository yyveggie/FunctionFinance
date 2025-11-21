'''
计算个股和市场的价格波动率
'''
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class VolatilityCalculator:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data = self._download_data()

    def _download_data(self):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        data = yf.download(self.symbol, start=start_date, end=end_date)
        return data

    def calculate_monthly_volatility(self):
        monthly_volatility = {}
        for i in range(6):
            end_of_month = datetime.now().replace(day=1) - timedelta(days=i*30)
            start_of_month = end_of_month.replace(day=1) - timedelta(days=30)
            mask = (self.data.index >= start_of_month) & (self.data.index < end_of_month)
            monthly_data = self.data.loc[mask]
            returns = pd.Series(np.diff(np.log(monthly_data['Close'])))
            volatility = round(returns.std() * np.sqrt(252), 4)
            monthly_volatility[end_of_month.strftime('%Y-%m')] = volatility
        return monthly_volatility

if __name__ == '__main__':
    symbol = "AAPL"  # 可以输入个股代码或指数代码
    volatility_calculator = VolatilityCalculator(symbol)
    monthly_volatility = volatility_calculator.calculate_monthly_volatility()
    print(monthly_volatility)
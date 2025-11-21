'''
通过计算个股在过去一段时间内的动量因子。
'''
import yfinance as yf
import pandas as pd
import datetime

class MomentumCalculator:
    def __init__(self, stock_data, benchmark_data):
        self.stock_data = stock_data
        self.benchmark_data = benchmark_data

    def calculate_returns(self, data):
        return data.pct_change().fillna(0)

    def calculate_excess_returns(self):
        stock_returns = self.calculate_returns(self.stock_data)
        benchmark_returns = self.calculate_returns(self.benchmark_data)
        excess_returns = stock_returns - benchmark_returns
        return excess_returns

    def calculate_momentum(self, period):
        """计算指定周期内的动量因子"""
        excess_returns = self.calculate_excess_returns()
        return excess_returns.rolling(window=period).mean().iloc[-1]

    def get_monthly_results(self):
        end_date = self.stock_data.index[-1]
        start_date = end_date - pd.DateOffset(months=5)

        momentum_factors = {}
        for i in range(6):
            period_end = end_date - pd.DateOffset(months=i)
            period_start = period_end - pd.DateOffset(months=1)
            period_data = self.stock_data.loc[period_start:period_end]
            period_benchmark_data = self.benchmark_data.loc[period_start:period_end]

            if not period_data.empty and not period_benchmark_data.empty:
                period_calculator = MomentumCalculator(period_data, period_benchmark_data)
                momentum_factor = period_calculator.calculate_momentum(len(period_data))
                momentum_factors[period_end.strftime('%Y-%m')] = round(momentum_factor, 4)

        return momentum_factors


if __name__ == '__main__':
    stock_symbol = 'BABA'
    index_symbol = '^SPX' # '^SPX':标普100, '^GSPC': 标普500

    end_date = datetime.date.today()
    start_date = end_date - pd.DateOffset(months=6)

    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)['Adj Close']
    market_data = yf.download(index_symbol, start=start_date, end=end_date)['Adj Close']

    calculator = MomentumCalculator(stock_data, market_data)
    monthly_momentum_factors = calculator.get_monthly_results()
    print(monthly_momentum_factors)
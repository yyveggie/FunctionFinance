'''
LSV 衡量标准：Lakonishok、Shleifer 和 Vishny (1992) 开发了一种量化机构投资者羊群行为的衡量标准。 它将投资者买入或卖出股票的实际比例与基于随机机会的预期比例进行比较。
'''
import yfinance as yf
import numpy as np

class LSVMeasure:
    def __init__(self, expected_buy_ratio=0.5):
        self.expected_buy_ratio = expected_buy_ratio
    
    def get_stock_data(self, data):
        close_prices = data['Close']
        return close_prices
    
    def calculate_returns(self, close_prices):
        returns = close_prices.pct_change().dropna()
        return returns
    
    def simulate_investor_behavior(self, returns):
        buy_sell_data = returns.apply(lambda x: 1 if x > 0 else 0)
        return buy_sell_data
    
    def calculate_actual_buy_ratio(self, buy_sell_data):
        actual_buy_ratio = buy_sell_data.mean()
        return actual_buy_ratio
    
    def calculate_lsv_index(self, actual_buy_ratio):
        lsv_index = np.abs(actual_buy_ratio - self.expected_buy_ratio)
        return lsv_index
    
    def run_analysis(self, data):
        close_prices = self.get_stock_data(data)
        returns = self.calculate_returns(close_prices)
        buy_sell_data = self.simulate_investor_behavior(returns)
        actual_buy_ratio = self.calculate_actual_buy_ratio(buy_sell_data)
        lsv_index = self.calculate_lsv_index(actual_buy_ratio)
        return lsv_index

# 使用示例
if __name__ == '__main__':
    symbol = '^SPX'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    
    lsv_measure = LSVMeasure(symbol, start_date, end_date)
    lsv_index = lsv_measure.run_analysis()
    print(f'LSV Index: {lsv_index}')
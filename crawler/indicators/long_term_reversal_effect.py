'''
长期反转效应：“涨久必跌、跌久必涨”，计算个股和市场长期涨跌情况
'''
import yfinance as yf
import pandas as pd
import datetime as dt

class LongTermReversalEffect:
    def __init__(self):
        self.periods = {
            "6 months": 6 * 21,  # 每个月大约有21个交易日
            "1 year": 12 * 21,
            "1.5 years": 18 * 21, 
            "2 years": 24 * 21,
            "2.5 years": 30 * 21,
            "3 years": 36 * 21
        }

    def calculate_returns(self, stock_data, period):
        if len(stock_data) >= period:
            start_price = stock_data['Close'].iloc[-period]
            end_price = stock_data['Close'].iloc[-1]
            return (end_price - start_price) / start_price
        else:
            return None  # 数据不足,无法计算

    def analyze_stocks(self, stock_data):
        result = {}
        for period_name, period_days in self.periods.items():
            returns = self.calculate_returns(stock_data, period_days)
            if returns is not None:
                result[period_name] = f"{returns*100:.2f}%"
            else:
                result[period_name] = "数据不足"
        return result

# 使用示例
if __name__ == "__main__":
    symbol = 'SPY'  # 可以替换为你感兴趣的股票和指数
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=3*365)
    analyzer = LongTermReversalEffect(symbol, start_date, end_date)
    result = analyzer.analyze_stocks()
    print(f"{symbol} 的涨跌情况:")
    print(result)
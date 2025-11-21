'''
惯性效应：股票在短期表现与长期完全相反——惯性！惯性，也就是原来涨的还会涨，原来跌的还会跌。
所以，短期交易策略为“追涨杀跌”。惯性交易策略，即追涨杀跌，利用的是投资者对股票市场上的信息反应不足这种心理偏差。
'''
import yfinance as yf
import pandas as pd
import datetime as dt

class InertiaEffect:
    def __init__(self, stock_data):
        self.stock_data = stock_data

    def calculate_monthly_returns(self, periods):
        returns = {}
        for period in periods:
            start_date, end_date = period
            month_data = self.stock_data[(self.stock_data.index >= start_date) & (self.stock_data.index < end_date)]
            if not month_data.empty:
                start_price = month_data['Close'].iloc[0]
                end_price = month_data['Close'].iloc[-1]
                returns[f"{start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')}"] = round((end_price - start_price) / start_price, 4)
            else:
                returns[f"{start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')}"] = None  # 数据不足,无法计算
        return returns

    def get_monthly_returns(self, months):
        # 获取数据的最新日期
        end_date = self.stock_data.index[-1]

        # 定义过去指定月数的起始和结束日期
        periods = []
        for i in range(months, 0, -1):
            start_date = (end_date - pd.DateOffset(months=i)).replace(day=1)
            end_date_next = (start_date + pd.DateOffset(months=1)).replace(day=1)
            periods.append((start_date, end_date_next))

        # 计算月涨跌情况
        returns = self.calculate_monthly_returns(periods)
        return returns

if __name__ == '__main__':
    # 使用示例
    symbol = '^SPX'  # 可以替换为你感兴趣的股票或指数
    start_date = '2022-01-01'
    end_date = dt.datetime.now().strftime('%Y-%m-%d')

    # 使用 yfinance 下载股票数据
    stock_data = yf.download(symbol, start=start_date, end=end_date)

    ie = InertiaEffect(stock_data)
    monthly_returns = ie.get_monthly_returns(6)

    print(monthly_returns)
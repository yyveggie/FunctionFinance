import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class CumulativeReturnCalculator:
    def __init__(self, data):
        self.data = data

    def calculate_cumulative_return(self, start_index, end_index):
        """计算指定时间段内的累计收益率"""
        start_price = self.data['Adj Close'].iloc[start_index]
        end_price = self.data['Adj Close'].iloc[end_index]
        cumulative_return = (end_price - start_price) / start_price
        return cumulative_return

    def get_results(self):
        cumulative_returns = {}

        # 获取数据的起始和结束日期
        start_date = self.data.index[0]
        end_date = self.data.index[-1]

        # 计算六个月前的日期
        six_months_ago = end_date - timedelta(days=180)

        # 如果数据的起始日期早于六个月前,则将起始日期调整为六个月前
        if start_date < six_months_ago:
            start_date = six_months_ago

        # 生成月份范围,包括结束日期所在的月份
        months = pd.date_range(start=start_date, end=end_date + pd.offsets.MonthEnd(), freq='M')

        for i in range(len(months) - 1):
            start_month = months[i]
            end_month = months[i + 1]

            # 获取月份范围内的数据索引
            mask = (self.data.index >= start_month) & (self.data.index <= end_month)
            month_data = self.data.loc[mask]

            if not month_data.empty:
                start_index = month_data.index[0]
                end_index = month_data.index[-1]
                cumulative_return = self.calculate_cumulative_return(self.data.index.get_loc(start_index),
                                                                     self.data.index.get_loc(end_index))
                cumulative_returns[f"{start_month.strftime('%Y-%m')}"] = round(cumulative_return, 4)

        return cumulative_returns


if __name__ == '__main__':
    stock_data = yf.download("BABA", start="2022-01-01", end="2023-06-04")
    calculator = CumulativeReturnCalculator(stock_data)
    cumulative_returns = calculator.get_results()
    print(cumulative_returns)
'''
计算恐慌指数vix
'''
import yfinance as yf
from typing import Union
from datetime import datetime

class VixData:
    def __init__(self, start_date: Union[str, datetime], end_date: Union[str, datetime]):
        self.start_date = start_date
        self.end_date = end_date
        self.vix_data = self._download_data()

    def _download_data(self):
        return yf.download('^VIX', start=self.start_date, end=self.end_date)

    def get_data(self):
        return self.vix_data

    def get_value_on_specific_date(self, date: Union[str, datetime]):
        return self.vix_data.loc[date, 'Close']

    def get_values_in_range(self, start_date: Union[str, datetime], end_date: Union[str, datetime]):
        return self.vix_data[start_date:end_date]

    def get_latest_value(self):
        return self.vix_data['Close'].iloc[-1]

    def get_close_series(self):
        return self.vix_data['Close']

if __name__ == '__main__':
    # 创建VixData对象,指定数据的起始和结束日期
    vix = VixData(start_date='2022-01-01', end_date='2023-05-30')

    # 获取整个时间范围内的VIX数据
    vix_data = vix.get_data()
    print(vix_data)

    # 获取特定日期的VIX值
    vix_value_on_specific_date = vix.get_value_on_specific_date('2023-01-03')
    print(f"VIX value on 2023-01-03: {vix_value_on_specific_date}")

    # 获取一段时间内的VIX值
    vix_values_in_january = vix.get_values_in_range('2023-01-01', '2023-01-31')
    print(vix_values_in_january)

    # 获取最新的VIX值
    latest_vix_value = vix.get_latest_value()
    print(f"Latest VIX value: {latest_vix_value}")

    # 提取VIX的收盘价时间序列
    vix_close_series = vix.get_close_series()
    print(vix_close_series)
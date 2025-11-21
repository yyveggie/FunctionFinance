'''
- 偏度(Skewness)：可以衡量收益分布的对称性，负偏度可能表明市场对负面信息反应过激。
- 峰度(Kurtosis)：可以衡量收益分布的峰度，高峰度可能表明市场存在过激反应。
'''
import yfinance as yf
from scipy.stats import skew, kurtosis
import datetime as dt

class SkewnessKurtosis(object):
    def __init__(self, data):
        self.data = data
    
    def calculate_skewness_kurtosis(self):
        daily_returns = self.data['Close'].pct_change().dropna()
        skewness = skew(daily_returns)
        kurt = kurtosis(daily_returns, fisher=True)  # 使用 Fisher 的定义，即正态分布的峰度为 0
        return skewness, kurt

if __name__ == '__main__':
    # 创建 StockAnalysis 类实例
    analysis = SkewnessKurtosis()

    # 计算偏度和峰度
    skewness, kurt = analysis.calculate_skewness_kurtosis()

    # 输出结果
    print(f"{ticker} 在过去一个月的偏度(Skewness): {skewness:.2f}")
    print(f"{ticker} 在过去一个月的峰度(Kurtosis): {kurt:.2f}")

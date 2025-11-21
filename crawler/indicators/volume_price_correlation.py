'''
计算交易量变化与股价之间的相关性。
'''
import yfinance as yf
from datetime import datetime, timedelta

class VolumePriceCorrelation:
    def __init__(self, stock_or_index):
        self.stock_or_index = stock_or_index
        self.correlations = None

    def calculate_correlations(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)  # 半年前的日期

        data = yf.download(self.stock_or_index, start=start_date, end=end_date)

        close_prices = data['Close']
        volumes = data['Volume']

        returns = close_prices.pct_change().dropna()
        volume_changes = volumes.diff().dropna()

        monthly_correlations = {}
        for month in range(6):
            month_end = end_date - timedelta(days=month*30)
            month_start = month_end - timedelta(days=30)

            month_returns = returns[(returns.index.date >= month_start) & (returns.index.date <= month_end)]
            month_volume_changes = volume_changes[(volume_changes.index.date >= month_start) & (volume_changes.index.date <= month_end)]

            correlation = round(month_volume_changes.corr(month_returns), 4)
            monthly_correlations[month_end.strftime('%Y-%m')] = correlation

        self.correlations = monthly_correlations

    def get_results(self):
        if self.correlations is None:
            self.calculate_correlations()

        return self.correlations

# 使用示例
stock_correlation = VolumePriceCorrelation('AAPL')  # 标普500指数
results = stock_correlation.get_results()
print(results)
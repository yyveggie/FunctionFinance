'''
计算个股收益率与市场指数收益率之间的皮尔逊相关系数,衡量了个股与整个市场的相关性。
'''
from scipy.stats import pearsonr
import yfinance as yf

class StockMarketCorrelation:
    def __init__(self, stock_symbol, market_index, start_date, end_date, stock_data, market_data):
        self.stock_symbol = stock_symbol
        self.market_index = market_index
        self.start_date = start_date
        self.end_date = end_date
        self.stock_data = stock_data
        self.market_data = market_data

    def calculate_returns(self):
        # 计算个股和市场指数的收益率
        self.stock_returns = self.stock_data['Adj Close'].pct_change()
        self.market_returns = self.market_data['Adj Close'].pct_change()

    def clean_data(self):
        # 清理数据,去除缺失值
        self.stock_returns.dropna(inplace=True)
        self.market_returns.dropna(inplace=True)

        # 确保个股和市场指数的时间范围一致
        common_dates = self.stock_returns.index.intersection(self.market_returns.index)
        self.stock_returns = self.stock_returns.loc[common_dates]
        self.market_returns = self.market_returns.loc[common_dates]

    def calculate_correlation(self):
        # 计算个股与市场的皮尔逊相关系数
        corr, _ = pearsonr(self.stock_returns, self.market_returns)
        self.correlation = corr
    
    def run(self):
        self.calculate_returns()
        self.clean_data()
        self.calculate_correlation()
        return self.correlation

# 使用示例
if __name__ == '__main__':
    stock_symbol = 'AAPL'  # 要分析的个股代码
    market_index = '^GSPC'  # 标准普尔500指数代码
    start_date = '2020-01-01'
    end_date = '2023-05-31'

    correlation_analyzer = StockMarketCorrelation(stock_symbol, market_index, start_date, end_date)
    result = correlation_analyzer.run()
    print(f"{stock_symbol}与{market_index}的皮尔逊相关系数: {result}")
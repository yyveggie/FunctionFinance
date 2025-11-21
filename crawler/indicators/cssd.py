'''
横截面标准差(CSSD)：该指标量化了单个资产回报与已实现市场平均水平的平均接近程度。
'''
import yfinance as yf

class CSSD:
    def __init__(self, stock, start_date, end_date, market_index='^GSPC'):
        self.stock = stock
        self.start_date = start_date
        self.end_date = end_date
        self.market_index = market_index

    def calculate(self):
        # 获取股票数据和市场指数数据
        stock_data = yf.download(self.stock, start=self.start_date, end=self.end_date)
        market_data = yf.download(self.market_index, start=self.start_date, end=self.end_date)

        # 只保留收盘价
        stock_close_prices = stock_data['Close']
        market_close_prices = market_data['Close']

        # 计算每日回报率
        stock_returns = stock_close_prices.pct_change().dropna()
        market_returns = market_close_prices.pct_change().dropna()

        # 计算股票回报率与市场回报率之间的偏差
        deviation = stock_returns - market_returns

        # 计算 CSSD
        cssd = deviation.std()

        return cssd

if __name__ == '__main__':
    # 使用示例
    stock = 'MSFT'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    cssd_calculator = CSSD(stock, start_date, end_date)
    cssd_result = cssd_calculator.calculate()
    print(f"CSSD for {stock}: {cssd_result:.4f}")
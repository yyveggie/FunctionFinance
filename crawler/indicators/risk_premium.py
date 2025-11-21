'''
风险溢价：损失厌恶会导致投资者要求更高的风险补偿。可以通过比较个股或市场的实际收益与风险溢价的差异,来判断损失厌恶的影响。可以进一步细化为市场风险溢价、个股风险溢价。
'''
import yfinance as yf
import numpy as np

class RiskPremium:
    def __init__(self, symbol, market_index):
        """
        初始化RiskPremium类
        
        参数:
        risk_free_rate (float): 无风险利率
        """
        self.symbol = symbol
        self.market_index = market_index
        self.period = "2y"  # 使用最近2年的数据
        self.interval = "1mo"

    def calculate_market_risk_premium(self):
        """
        计算市场风险溢价
        
        参数:
        market_index (str): 市场指数代码
        period (str): 数据时间范围
        interval (str): 数据频率
        
        返回:
        float: 市场风险溢价
        """
        market_data = yf.download(self.market_index, period=self.period, interval=self.interval)
        market_returns = market_data["Adj Close"].pct_change().dropna()
        risk_free_rate = get_risk_free_rate(self.period, self.interval)
        return np.mean(market_returns) - risk_free_rate

    def calculate_stock_risk_premium(self):
        """
        计算个股风险溢价
        
        参数:
        stock_symbol (str): 股票代码
        market_index (str): 市场指数代码
        period (str): 数据时间范围
        interval (str): 数据频率
        
        返回:
        float: 个股风险溢价
        """
        stock_data = yf.download(self.symbol, period=self.period, interval=self.interval)
        market_data = yf.download(self.market_index, period=self.period, interval=self.interval)
        
        stock_returns = stock_data["Adj Close"].pct_change().dropna()
        market_returns = market_data["Adj Close"].pct_change().dropna()
        
        beta = self._calculate_beta(stock_returns, market_returns)
        market_risk_premium = self.calculate_market_risk_premium()
        
        return beta * market_risk_premium

    def _calculate_beta(self, stock_returns, market_returns):
        """
        计算贝塔系数
        
        参数:
        stock_returns (pd.Series): 股票收益率
        market_returns (pd.Series): 市场收益率
        
        返回:
        float: 贝塔系数
        """
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance

def get_risk_free_rate(period, interval):
    """
    获取无风险利率
    
    参数:
    period (str): 数据时间范围
    interval (str): 数据频率
    
    返回:
    float: 无风险利率
    """
    risk_free_rate_symbol = "^TNX"  # 10-Year Treasury Yield
    risk_free_data = yf.download(risk_free_rate_symbol, period=period, interval=interval)
    risk_free_rate = risk_free_data["Adj Close"].mean() / 100  # 转换为小数形式
    return risk_free_rate

if __name__ == "__main__":
    symbol = "AAPL"
    market_index = "^GSPC"
    rp = RiskPremium(symbol, market_index)
    
    market_risk_premium = rp.calculate_market_risk_premium()
    print(f"Market Risk Premium: {market_risk_premium:.4f}")
    
    stock_risk_premium = rp.calculate_stock_risk_premium()
    print(f"Stock Risk Premium for {symbol}: {stock_risk_premium:.4f}")
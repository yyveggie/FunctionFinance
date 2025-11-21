'''
下行风险：损失厌恶的投资者对下行风险更加敏感。可以用个股或市场在下跌期间的表现，如最大回撤、下行波动率，下行β系数等指标来度量。
'''
import numpy as np
import pandas as pd
import yfinance as yf

class DownsideRiskCalculator:
    
    @staticmethod
    def downside_risk_metrics(returns, benchmark_returns, risk_free_rate=0.0):
        """计算下行风险指标"""
        excess_returns = returns - risk_free_rate
        excess_benchmark_returns = benchmark_returns - risk_free_rate

        # 删除缺失值
        excess_returns = excess_returns.dropna()
        excess_benchmark_returns = excess_benchmark_returns.dropna()

        cumulative_returns = (1 + excess_returns).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()

        downside_returns = excess_returns[excess_returns < 0]
        downside_volatility = np.std(downside_returns) * np.sqrt(252)

        # 计算下行协方差和下行方差
        downside_covariance = np.cov(downside_returns, excess_benchmark_returns.loc[downside_returns.index])[0, 1]
        downside_variance = np.var(excess_benchmark_returns[downside_returns.index])
        downside_beta = downside_covariance / downside_variance if downside_variance != 0 else np.nan

        return {
            'max_drawdown': max_drawdown,
            'downside_volatility': downside_volatility,
            'downside_beta': downside_beta
        }
    
    def calculate_stock_risk(self, stock_ticker, benchmark_ticker, start_date, end_date):
        """计算个股的下行风险指标"""
        # 获取历史数据
        stock_data = yf.download(stock_ticker, start=start_date, end=end_date)
        benchmark_data = yf.download(benchmark_ticker, start=start_date, end=end_date)

        # 计算收益率序列
        stock_returns = stock_data['Adj Close'].pct_change()
        benchmark_returns = benchmark_data['Adj Close'].pct_change()

        # 计算个股下行风险指标
        stock_risk_metrics = self.downside_risk_metrics(stock_returns, benchmark_returns)

        return stock_risk_metrics
    
    def calculate_market_risk(self, market_ticker, start_date, end_date, risk_free_rate=0.0):
        """计算市场的下行风险指标"""
        # 获取历史数据
        market_data = yf.download(market_ticker, start=start_date, end=end_date)

        # 计算收益率序列
        market_returns = market_data['Adj Close'].pct_change()

        # 计算市场下行风险指标
        market_risk_metrics = self.downside_risk_metrics(market_returns, market_returns, risk_free_rate)

        return market_risk_metrics

# 使用示例
calculator = DownsideRiskCalculator()

# 指定中国股票代码和基准代码
stock_ticker = '600519.SS'  # 茅台股票代码
benchmark_ticker = '000300.SS'  # 沪深300指数代码

# 获取下行风险指标
stock_risk_metrics = calculator.calculate_stock_risk(stock_ticker, benchmark_ticker, '2022-01-01', '2023-04-30')

print(f"{stock_ticker} 下行风险指标:")
print(f"最大回撤: {stock_risk_metrics['max_drawdown']:.2%}")
print(f"下行波动率: {stock_risk_metrics['downside_volatility']:.2%}")
print(f"下行β系数: {stock_risk_metrics['downside_beta']:.2f}")

# 获取市场下行风险指标
market_risk_metrics = calculator.calculate_market_risk(benchmark_ticker, '2022-01-01', '2023-04-30')

print(f"{benchmark_ticker} 市场下行风险指标:")
print(f"最大回撤: {market_risk_metrics['max_drawdown']:.2%}")
print(f"下行波动率: {market_risk_metrics['downside_volatility']:.2%}")


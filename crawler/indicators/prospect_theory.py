'''
基于前景理论的框架,通过计算价值函数和概率权重函数,量化了投资者对收益和损失的非线性偏好。
通过比较市场指数和个股在收益和损失时的主观价值差异,计算得出了它们各自的损失厌恶系数,从而刻画了投资者对风险的非理性态度。
代码中的参数(α、β、λ、γ、δ)可以根据实证研究或特定需求进行调整,以反映个体差异。它假设所有投资者都有相同的参数值,而实际上个体差异可能很大。
'''
import numpy as np
import yfinance as yf
from scipy.stats import norm

params = {
        'alpha': 0.88,
        'beta': 0.88, 
        'lambd': 2.25,
        'gamma': 0.61,
        'delta': 0.69
    }

def prospect_theory_value(x, alpha=0.88, beta=0.88, lambd=2.25):
    return x.clip(lower=0)**alpha - lambd*(-x.clip(upper=0))**beta

def weighting_function(p, gamma=0.61, delta=0.69):
    return p**gamma / (p**gamma + (1 - p)**gamma)**(1/gamma)

def cum_prospect_theory(returns, ref, alpha=0.88, beta=0.88, lambd=2.25, gamma=0.61, delta=0.69):
    returns = returns - ref
    returns = returns[~np.isnan(returns)]  # 移除 nan 值
    value = prospect_theory_value(returns, alpha, beta, lambd)
    sorted_returns = returns.sort_values()
    cdf = norm.cdf(sorted_returns, loc=np.nanmean(returns), scale=np.nanstd(returns))
    weights = np.diff(weighting_function(cdf, gamma, delta), prepend=0)
    
    return np.nansum(value * weights)

def loss_aversion(returns, ref, alpha=0.88, beta=0.88, lambd=2.25, gamma=0.61, delta=0.69):
    returns = returns[~np.isnan(returns)]  # 移除 nan 值
    gains = returns[returns >= ref]
    losses = returns[returns < ref]
    
    if len(gains) == 0 or len(losses) == 0:
        return 1  # 当没有收益或损失时,返回中性值 1
    
    return -cum_prospect_theory(losses, ref, alpha, beta, lambd, gamma, delta) / cum_prospect_theory(gains, ref, alpha, beta, lambd, gamma, delta)


def run(data):
    returns = data['Adj Close'].pct_change().dropna()
    ref = returns.rolling(252).mean().iloc[-1]
    market_la = loss_aversion(returns, ref, **params)
    return f"Loss Aversion (ref={ref:.4f}): {market_la:.2f}"

if __name__ == '__main__':
    symbol = 'AAPL'
    start='2024-01-01'
    end='2024-05-31'
    
    print(run(symbol, start, end))
import yfinance as yf
import pandas as pd
import numpy as np

# 定义中国股票列表和时间范围
stocks = ['600519.SS', '000001.SZ', '000651.SZ', '300750.SZ', '601318.SS']  # 茅台、平安银行、美的集团、宁德时代、中国平安
start_date = '2023-01-01'
end_date = '2023-12-31'

# 获取股票数据
data = yf.download(stocks, start=start_date, end=end_date)

# 只保留收盘价
close_prices = data['Close']

# 计算每日回报率
returns = close_prices.pct_change().dropna()

# 计算市场平均回报率
market_mean_return = returns.mean(axis=1)

# 计算每只股票的回报率与市场平均回报率之间的偏差
deviation = returns.subtract(market_mean_return, axis=0)

# 计算每日 CSSD
cssd = deviation.std(axis=1)

# 将结果转换为 DataFrame 以便于展示
cssd_df = pd.DataFrame(cssd, columns=['CSSD'])
print(cssd_df)

'''
计算个股的隐含波动率指标。
'''
import yfinance as yf
import numpy as np
from scipy.stats import norm
import pandas as pd

def get_nearest_monthly_expiry(symbol):
    ticker = yf.Ticker(symbol)
    expiry_dates = ticker.options  # 获取所有可用的到期日
    
    if not expiry_dates:
        raise ValueError("No expiry dates found for the given symbol.")
    
    # 找到最近的月度期权到期日
    today = pd.Timestamp.today()
    expiry_dates = pd.to_datetime(expiry_dates)
    expiry_dates = expiry_dates[expiry_dates > today]  # 只保留未来的到期日
    
    if len(expiry_dates) == 0:
        raise ValueError("No future expiry dates found for the given symbol.")
    
    nearest_expiry = expiry_dates.min()
    return nearest_expiry.strftime("%Y-%m-%d")  # 直接返回字符串格式的日期

def implied_volatility(option_price, stock_price, strike_price, time_to_expiry, risk_free_rate, option_type):
    """
    Calculate implied volatility using Black-Scholes model
    """
    def bs_price(volatility):
        d1 = (np.log(stock_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        if option_type == 'call':
            price = stock_price * norm.cdf(d1) - strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
        else:
            price = strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - stock_price * norm.cdf(-d1)
        return price

    implied_vol = 0.5
    max_iterations = 100
    tolerance = 1e-4

    for i in range(max_iterations):
        option_price_implied = bs_price(implied_vol)
        d1 = (np.log(stock_price / strike_price) + (risk_free_rate + 0.5 * implied_vol ** 2) * time_to_expiry) / (implied_vol * np.sqrt(time_to_expiry))
        vega = stock_price * norm.pdf(d1) * np.sqrt(time_to_expiry)
        implied_vol -= (option_price_implied - option_price) / vega
        if abs(option_price_implied - option_price) < tolerance:
            break

    return implied_vol

def get_monthly_implied_volatility(symbol):
    results = {}
    ticker = yf.Ticker(symbol)
    expiry_date = get_nearest_monthly_expiry(symbol)
    expiry_date = pd.to_datetime(expiry_date)  # 将字符串格式的日期转换为Timestamp格式
    
    try:
        options = ticker.option_chain(expiry_date.strftime("%Y-%m-%d"))  # 将Timestamp格式转换为字符串格式
        calls = options.calls
        puts = options.puts

        # 数据预处理
        calls = calls[calls['volume'] > 0]  # 只保留成交量大于0的期权
        puts = puts[puts['volume'] > 0]

        if len(calls) == 0 or len(puts) == 0:
            raise ValueError("No valid option data found for the given expiry date.")

        risk_free_rate = 0.02  # 无风险利率,可以根据实际情况调整
        stock_price = ticker.history(period='1d')['Close'].iloc[-1]
        time_to_expiry = (expiry_date - pd.Timestamp.today()).days / 365

        call_implied_vols = []
        put_implied_vols = []

        for _, row in calls.iterrows():
            if row['lastPrice'] > 0 and row['strike'] > 0:  # 只处理价格和行权价大于0的期权
                call_implied_vol = implied_volatility(row['lastPrice'], stock_price, row['strike'], time_to_expiry, risk_free_rate, 'call')
                if not np.isnan(call_implied_vol):  # 忽略NaN结果
                    call_implied_vols.append(call_implied_vol)

        for _, row in puts.iterrows():
            if row['lastPrice'] > 0 and row['strike'] > 0:
                put_implied_vol = implied_volatility(row['lastPrice'], stock_price, row['strike'], time_to_expiry, risk_free_rate, 'put')
                if not np.isnan(put_implied_vol):
                    put_implied_vols.append(put_implied_vol)

        if len(call_implied_vols) == 0 or len(put_implied_vols) == 0:
            raise ValueError("No valid implied volatilities found for the given expiry date.")

        average_call_implied_vol = np.mean(call_implied_vols)
        average_put_implied_vol = np.mean(put_implied_vols)
        results["最近的月度期权到期日"] = expiry_date
        results["平均看涨期权隐含波动率"] = average_call_implied_vol
        results["平均看跌期权隐含波动率"] = average_put_implied_vol
        return results

    except ValueError as e:
        print(f"Error: {str(e)}")
        return None, None, None

if __name__ == "__main__":
    # 示例用法
    symbol = "SPY"  # 苹果公司股票代码
    results = get_monthly_implied_volatility(symbol)
    print(results)
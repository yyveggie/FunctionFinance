'''
这段代码用于分析市场指数或个股的隐含波动率指标。
它利用Heston模型和数值优化方法计算隐含波动率,
并通过分析看涨期权和看跌期权的隐含波动率差异、偏度和曲面,来评估市场或个股的风险厌恶程度和预期波动性。
'''
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import curve_fit, least_squares
from scipy.integrate import quad, IntegrationWarning
import warnings

warnings.simplefilter('ignore', IntegrationWarning)

class HestonModel:
    def __init__(self, risk_free_rate, kappa, theta, sigma, rho, v0):
        self.risk_free_rate = risk_free_rate
        self.kappa = kappa
        self.theta = theta
        self.sigma = sigma
        self.rho = rho
        self.v0 = v0

    def characteristic_function(self, phi, S, v, tau):
        gamma = np.sqrt(self.sigma**2 * (phi**2 + phi * 1j) + (self.kappa - self.rho * self.sigma * phi * 1j)**2)
        g = (self.kappa - self.rho * self.sigma * phi * 1j - gamma) / (self.kappa - self.rho * self.sigma * phi * 1j + gamma)
        C = self.risk_free_rate * phi * 1j * tau + self.kappa * self.theta / self.sigma**2 * (
            (self.kappa - self.rho * self.sigma * phi * 1j - gamma) * tau - 2 * np.log((1 - g * np.exp(-gamma * tau)) / (1 - g)))
        D = (self.kappa - self.rho * self.sigma * phi * 1j - gamma) / self.sigma**2 * ((1 - np.exp(-gamma * tau)) / (1 - g * np.exp(-gamma * tau)))
        return np.exp(C + D * v + 1j * phi * np.log(S))

    def call_price(self, S, K, v, tau):
        integrand = lambda phi: (np.exp(-1j * phi * np.log(K)) * self.characteristic_function(phi - 1j, S, v, tau) / (1j * phi * self.characteristic_function(-1j, S, v, tau))).real
        integral, _ = quad(integrand, 0, np.inf, limit=100)
        return S - np.sqrt(S * K) / np.pi * integral

    def put_price(self, S, K, v, tau):
        integrand = lambda phi: (np.exp(-1j * phi * np.log(K)) * self.characteristic_function(phi, S, v, tau) / (-1j * phi)).real
        integral, _ = quad(integrand, 0, np.inf, limit=100)
        return np.sqrt(S * K) / np.pi * integral - S + K * np.exp(-self.risk_free_rate * tau)

    def implied_volatility(self, option_price, S, K, tau, option_type, initial_guess=0.2, bounds=(1e-5, 1)):
        if option_type == 'call':
            pricing_function = self.call_price
        elif option_type == 'put':
            pricing_function = self.put_price
        else:
            raise ValueError("Invalid option type. Must be 'call' or 'put'.")

        def objective(v):
            return pricing_function(S, K, v, tau) - option_price

        res = least_squares(objective, initial_guess, bounds=bounds)
        return res.x[0]

class MarketRiskAversion:
    def __init__(self, symbol, risk_free_rate, kappa=2, theta=0.04, sigma=0.3, rho=-0.7, v0=0.04):
        self.symbol = symbol
        self.heston_model = HestonModel(risk_free_rate, kappa, theta, sigma, rho, v0)
    
    def filter_strike_prices(self, options, n=10):
        options = options.sort_values(by='volume', ascending=False)
        strike_prices = options['strike'].unique()[:n]
        return strike_prices

    def analyze_implied_volatility(self, expiry_date, n=10):
        ticker = yf.Ticker(self.symbol)
        options = ticker.option_chain(expiry_date)
        calls = options.calls
        puts = options.puts

        call_strike_prices = self.filter_strike_prices(calls, n)
        put_strike_prices = self.filter_strike_prices(puts, n)
        
        stock_price = ticker.history(period='1d')['Close'].iloc[-1]
        time_to_expiry = (pd.to_datetime(expiry_date) - pd.Timestamp.today()).days / 365

        call_implied_vols = []
        put_implied_vols = []

        for strike in call_strike_prices:
            call = calls[calls['strike'] == strike].iloc[0]
            call_implied_vol = self.heston_model.implied_volatility(call['lastPrice'], stock_price, strike, time_to_expiry, 'call')
            if not np.isnan(call_implied_vol):
                call_implied_vols.append(call_implied_vol)

        for strike in put_strike_prices:
            put = puts[puts['strike'] == strike].iloc[0]
            put_implied_vol = self.heston_model.implied_volatility(put['lastPrice'], stock_price, strike, time_to_expiry, 'put')
            if not np.isnan(put_implied_vol):
                put_implied_vols.append(put_implied_vol)

        if len(call_implied_vols) == 0 or len(put_implied_vols) == 0:
            return np.nan, np.nan

        call_implied_vol_avg = np.mean(call_implied_vols)
        put_implied_vol_avg = np.mean(put_implied_vols)

        return call_implied_vol_avg, put_implied_vol_avg

    def analyze_implied_volatility_skew(self, expiry_date):
        ticker = yf.Ticker(self.symbol)
        options = ticker.option_chain(expiry_date)
        puts = options.puts

        stock_price = ticker.history(period='1d')['Close'].iloc[-1]
        time_to_expiry = (pd.to_datetime(expiry_date) - pd.Timestamp.today()).days / 365

        put_ivs = []
        put_strikes = []

        for _, row in puts.iterrows():
            put_iv = self.heston_model.implied_volatility(row['lastPrice'], stock_price, row['strike'], time_to_expiry, 'put')
            if not np.isnan(put_iv):
                put_ivs.append(put_iv)
                put_strikes.append(row['strike'])

        put_strikes = np.array(put_strikes)
        put_ivs = np.array(put_ivs)

        valid_indices = ~np.isnan(put_ivs) & ~np.isinf(put_ivs)
        put_strikes = put_strikes[valid_indices]
        put_ivs = put_ivs[valid_indices]

        if len(put_strikes) < 2:
            return np.nan

        def linear_func(x, a, b):
            return a * x + b

        popt, _ = curve_fit(linear_func, put_strikes, put_ivs)

        return popt[0]

    def analyze_implied_volatility_surface(self, expiry_dates):
        ticker = yf.Ticker(self.symbol)
        iv_surface = {}

        for expiry_date in expiry_dates:
            options = ticker.option_chain(expiry_date)
            calls = options.calls
            puts = options.puts

            stock_price = ticker.history(period='1d')['Close'].iloc[-1]
            time_to_expiry = (pd.to_datetime(expiry_date) - pd.Timestamp.today()).days / 365

            iv_data = {}

            for _, row in calls.iterrows():
                call_iv = self.heston_model.implied_volatility(row['lastPrice'], stock_price, row['strike'], time_to_expiry, 'call')
                if not np.isnan(call_iv):
                    iv_data[row['strike']] = call_iv

            for _, row in puts.iterrows():
                put_iv = self.heston_model.implied_volatility(row['lastPrice'], stock_price, row['strike'], time_to_expiry, 'put')
                if not np.isnan(put_iv):
                    iv_data[row['strike']] = put_iv

            iv_surface[expiry_date] = iv_data

        return iv_surface

def get_risk_free_rate(period='1y', interval='1d'):
    risk_free_rate_symbol = "^TNX"  # 10-Year Treasury Yield
    risk_free_data = yf.download(risk_free_rate_symbol, period=period, interval=interval)
    risk_free_rate = risk_free_data["Adj Close"].mean() / 100  # 将百分比转换为小数
    return risk_free_rate

def get_available_expiry_dates(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.options

# 示例用法
if __name__ == "__main__":
    symbol = "600519.SS"  # 茅台股票代码

    available_expiry_dates = get_available_expiry_dates(symbol)
    if not available_expiry_dates:
        print("No available expiry dates found.")
    else:
        print("Available expiry dates:", available_expiry_dates)

        expiry_date = available_expiry_dates[0]  # 使用第一个可用的到期日
        expiry_dates = available_expiry_dates[:3]  # 使用前三个可用的到期日
    
        risk_free_rate = get_risk_free_rate()
        market_risk_aversion = MarketRiskAversion(symbol, risk_free_rate)
        
        # 分析隐含波动率
        call_iv_avg, put_iv_avg = market_risk_aversion.analyze_implied_volatility(expiry_date)
        print(f"平均看涨期权隐含波动率: {call_iv_avg}")
        print(f"平均看跌期权隐含波动率: {put_iv_avg}")
        
        # 分析隐含波动率斜率
        iv_skew = market_risk_aversion.analyze_implied_volatility_skew(expiry_date)
        print(f"隐含波动率斜率: {iv_skew}")
        
        # 分析隐含波动率表面
        iv_surface = market_risk_aversion.analyze_implied_volatility_surface(expiry_dates)
        for expiry, surface in iv_surface.items():
            print(f"到期日: {expiry}")
            for strike, iv in surface.items():
                print(f"行权价: {strike}, 隐含波动率: {iv}")

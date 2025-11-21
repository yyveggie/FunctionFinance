'''
过度交易：不仅是交易频率，还可以结合交易金额和交易时点。
'''
import numpy as np
import scipy.stats as stats

class OverTradingAnalysis:
    def __init__(self, stock_data, benchmark_data):
        self.stock_data = stock_data
        self.benchmark_data = benchmark_data
        self.trading_days_per_month = 21

    def calculate_overtrading_metrics(self):
        if self.stock_data is None or self.benchmark_data is None:
            raise ValueError("Stock data or benchmark data is not loaded. Please load the data first using get_stock_data method.")

        # 计算日均交易量
        average_daily_volume = self.stock_data['Volume'].mean()
        benchmark_average_daily_volume = self.benchmark_data['Volume'].mean()
        
        # 计算总交易量
        total_volume = self.stock_data['Volume'].sum()
        benchmark_total_volume = self.benchmark_data['Volume'].sum()
        
        # 计算交易频率
        total_days = (self.stock_data.index[-1] - self.stock_data.index[0]).days + 1
        trading_days = len(self.stock_data)
        trading_frequency = trading_days / total_days
        benchmark_trading_frequency = len(self.benchmark_data) / total_days
        
        # 计算日均交易金额
        self.stock_data['Amount'] = self.stock_data['Close'] * self.stock_data['Volume']
        self.benchmark_data['Amount'] = self.benchmark_data['Close'] * self.benchmark_data['Volume']
        average_daily_amount = self.stock_data['Amount'].mean()
        benchmark_average_daily_amount = self.benchmark_data['Amount'].mean()
        relative_average_daily_amount = average_daily_amount / benchmark_average_daily_amount

        # 过滤异常交易日
        max_turnover_rate = self.stock_data['Volume'].rolling(window=self.trading_days_per_month).mean().max() * 0.1  # 假设换手率超过过去一个月平均水平的10%为异常
        self.stock_data['TurnoverRate'] = self.stock_data['Volume'] / self.stock_data['Volume'].rolling(window=self.trading_days_per_month).mean()
        mask = (self.stock_data['TurnoverRate'] < max_turnover_rate) & (~self.stock_data['Volume'].isnull())
        filtered_stock_data = self.stock_data.loc[mask]
        filtered_average_daily_volume = filtered_stock_data['Volume'].mean() if len(filtered_stock_data) > 0 else np.nan
        
        return average_daily_volume, total_volume, trading_frequency, benchmark_average_daily_volume, benchmark_total_volume, benchmark_trading_frequency, relative_average_daily_amount, filtered_average_daily_volume

    def calculate_overtrading_index(self, average_daily_volume, total_volume, trading_frequency, benchmark_average_daily_volume, benchmark_total_volume, benchmark_trading_frequency, relative_average_daily_amount, filtered_average_daily_volume):
        # 相对日均交易量
        relative_average_daily_volume = average_daily_volume / benchmark_average_daily_volume if benchmark_average_daily_volume != 0 else np.nan
        # 相对总交易量  
        relative_total_volume = total_volume / benchmark_total_volume if benchmark_total_volume != 0 else np.nan
        # 相对交易频率
        relative_trading_frequency = trading_frequency / benchmark_trading_frequency if benchmark_trading_frequency != 0 else np.nan
        # 将过滤后的日均交易量纳入计算
        filtered_relative_average_daily_volume = filtered_average_daily_volume / benchmark_average_daily_volume if benchmark_average_daily_volume != 0 else np.nan

        # 指标加权,权重可以根据实际情况调整
        weights = [0.3, 0.2, 0.2, 0.2, 0.1] 
        factors = [relative_total_volume, relative_trading_frequency, relative_average_daily_volume, filtered_relative_average_daily_volume, relative_average_daily_amount]
        
        weighted_factors = [weight * factor for weight, factor in zip(weights, factors)]
        valid_weighted_factors = [factor for factor in weighted_factors if not np.isnan(factor)]
        
        if len(valid_weighted_factors) == 0:
            overtrading_index = np.nan
        else:
            overtrading_index = stats.hmean(valid_weighted_factors) 
            
        return overtrading_index
    
    def run(self):
        # 计算过度交易的指标
        average_daily_volume, total_volume, trading_frequency, benchmark_average_daily_volume, benchmark_total_volume, benchmark_trading_frequency, relative_average_daily_amount, filtered_average_daily_volume  = self.calculate_overtrading_metrics()
        # 计算过度交易指数
        overtrading_index = self.calculate_overtrading_index(average_daily_volume, total_volume, trading_frequency, benchmark_average_daily_volume, benchmark_total_volume, benchmark_trading_frequency, relative_average_daily_amount, filtered_average_daily_volume)

        # 判断过度交易
        if overtrading_index > 1.5:
            overtrading_degree = "重度过度交易"
        elif overtrading_index > 1.2:
            overtrading_degree = "中度过度交易"  
        elif overtrading_index > 1:
            overtrading_degree = "轻度过度交易"
        else:
            overtrading_degree = "交易正常"

        output_dict = {
            '过去一个月的过度交易指数': f'{overtrading_index:.2f}',
            '过度交易程度': overtrading_degree,
            '日均交易量': average_daily_volume,
            '总交易量': total_volume,
            '交易频率': round(trading_frequency, 4)
        }
        return output_dict

if __name__ == '__main__':
    # 示例用法
    ticker = 'AAPL'  # 可以替换为你感兴趣的股票
    benchmark_ticker = 'SPY'  # 指数作为基准

    analysis = OverTradingAnalysis(ticker, benchmark_ticker)
    print(analysis.run())
'''
"击鼓传花"现象的量化分析基于以下两个主要原则:
- 短期交易频繁:在"击鼓传花"期间,投资者倾向于快速买入和卖出股票,以期在短期内获利。为了捕捉这种行为,我们计算了短期(如5天)的平均交易量变化和收益率。如果这些指标显著高于正常水平,则可能表明投资者正在进行频繁的短期交易。
- 交易量异常放大:在"击鼓传花"期间,股票的交易量往往会显著高于长期平均水平。这可能反映了投资者的过度兴奋和对短期利润的追逐。为了量化这一点,我们将短期平均交易量与长期(如20天)平均交易量进行比较,并设定一个阈值(如1.5倍)来识别交易量的异常放大。
'''
import yfinance as yf
import pandas as pd
import datetime as dt

class GreaterFoolTheoryAnalysis:
    CLOSE_COLUMN = 'Close'
    VOLUME_COLUMN = 'Volume'

    def __init__(self, data, short_window=7, long_window=20, volume_change_threshold=1.4, return_threshold=0.03):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.volume_change_threshold = volume_change_threshold
        self.return_threshold = return_threshold
        self.metrics = None
        self.greater_fool_periods = None

    def calculate_metrics(self):
        if self.data is None:
            raise ValueError("Stock data is not loaded. Please load the data first using get_stock_data method.")

        daily_return = self.data[self.CLOSE_COLUMN].pct_change()
        volume_change = self.data[self.VOLUME_COLUMN].pct_change()
        short_term_volume_change = volume_change.rolling(window=self.short_window, min_periods=1).mean()
        short_term_return = daily_return.rolling(window=self.short_window, min_periods=1).mean()
        long_term_average_volume = self.data[self.VOLUME_COLUMN].rolling(window=self.long_window, min_periods=1).mean()

        self.metrics = pd.DataFrame({
            'Daily Return': daily_return,
            'Volume Change': volume_change,
            'Short Term Volume Change': short_term_volume_change,
            'Short Term Return': short_term_return,
            'Long Term Average Volume': long_term_average_volume
        })

        return self.metrics

    def detect_greater_fool_conditions(self):
        if self.metrics is None:
            raise ValueError("Metrics are not calculated. Please calculate the metrics first using calculate_metrics method.")

        conditions = (self.metrics['Short Term Volume Change'] > self.volume_change_threshold) & (self.metrics['Short Term Return'].abs() > self.return_threshold)
        volume_conditions = self.data[self.VOLUME_COLUMN] > self.metrics['Long Term Average Volume']
        self.greater_fool_periods = conditions & volume_conditions

        return self.greater_fool_periods

    def generate_output(self):
        if self.greater_fool_periods is None:
            raise ValueError("Greater Fool periods are not detected. Please detect the periods first using detect_greater_fool_conditions method.")

        output = self.greater_fool_periods.any()
        return output

def greater_fool_theory_analysis(data, short_window=10, long_window=30, volume_change_threshold=1.5, return_threshold=0.03):
    """
    对指定的股票或指数进行"击鼓传花"现象的量化分析。

    参数:
    - ticker: 股票或指数代码的字符串
    - start_date: 分析的开始日期
    - end_date: 分析的结束日期
    - short_window: 计算短期指标的时间窗口,默认为10个交易日
    - long_window: 计算长期平均交易量的时间窗口,默认为30个交易日
    - volume_change_threshold: 识别交易量异常放大的阈值,默认为1.5(即短期平均交易量是长期平均交易量的1.5倍以上)
    - return_threshold: 识别短期异常收益率的阈值,默认为0.03(即短期平均收益率的绝对值大于3%)

    返回值:
    - 一个布尔值,表示是否检测到"击鼓传花"现象
    """

    analysis = GreaterFoolTheoryAnalysis(data, short_window, long_window, volume_change_threshold, return_threshold)
    analysis.calculate_metrics()
    analysis.detect_greater_fool_conditions()
    output = analysis.generate_output()

    return output

if __name__ == "__main__":
    # 示例用法
    ticker = 'AAPL'  # 可以替换为你感兴趣的股票或指数代码

    data = yf.download(ticker, start="2024-04-05", end="2024-05-05")
    # 进行"击鼓传花"现象的量化分析
    output = greater_fool_theory_analysis(data)

    # 打印结果
    print(f"{ticker}: Greater Fool Phenomenon {'Detected' if output else 'Not Detected'}")
'''
赢家/输家效应：损失厌恶可能导致投资者过早止盈和过晚止损。可以比较个股在上涨和下跌趋势中的持有时间和交易量差异,来捕捉这种非对称性。
'''
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

class WinnerLoser:
    def __init__(self, symbol):
        self.symbol = symbol
        self.end_date = datetime.now().date()
        self.start_date = self.end_date - relativedelta(months=6)
        self.stock_data = self.get_stock_data()

    def get_stock_data(self):
        return yf.download(self.symbol, start=self.start_date, end=self.end_date)

    def winner_loser_effect(self, window=20, min_trading_days=5):
        stock_data = self.stock_data.copy()
        stock_data['Returns'] = stock_data['Adj Close'].pct_change()

        stock_data['UpTrend'] = (stock_data['Returns'].rolling(window=window).mean() > 0).astype(int)
        stock_data['DownTrend'] = (stock_data['Returns'].rolling(window=window).mean() < 0).astype(int)

        stock_data['UpDuration'] = stock_data.groupby((stock_data['UpTrend'] != stock_data['UpTrend'].shift(1)).cumsum()).cumcount() + 1
        stock_data['DownDuration'] = stock_data.groupby((stock_data['DownTrend'] != stock_data['DownTrend'].shift(1)).cumsum()).cumcount() + 1

        stock_data['Month'] = pd.to_datetime(stock_data.index).strftime('%Y-%m')

        monthly_metrics = {}
        for month in stock_data['Month'].unique():
            monthly_data = stock_data[stock_data['Month'] == month]

            if len(monthly_data) < min_trading_days:
                monthly_metrics[month] = {
                    '上涨趋势平均持有时间': 'Insufficient data',
                    '下跌趋势平均持有时间': 'Insufficient data',
                    '上涨趋势平均交易量': 'Insufficient data',
                    '下跌趋势平均交易量': 'Insufficient data',
                    '备注': f'Only {len(monthly_data)} trading days in this month'
                }
                continue

            avg_up_duration = monthly_data[monthly_data['UpTrend'] == 1]['UpDuration'].mean()
            avg_down_duration = monthly_data[monthly_data['DownTrend'] == 1]['DownDuration'].mean()
            avg_up_volume = monthly_data[monthly_data['UpTrend'] == 1]['Volume'].mean()
            avg_down_volume = monthly_data[monthly_data['DownTrend'] == 1]['Volume'].mean()

            monthly_metrics[month] = {
                '上涨趋势平均持有时间': avg_up_duration if not pd.isna(avg_up_duration) else 'No uptrend',
                '下跌趋势平均持有时间': avg_down_duration if not pd.isna(avg_down_duration) else 'No downtrend',
                '上涨趋势平均交易量': avg_up_volume if not pd.isna(avg_up_volume) else 'No uptrend',
                '下跌趋势平均交易量': avg_down_volume if not pd.isna(avg_down_volume) else 'No downtrend',
                '备注': 'Current month' if month == self.end_date.strftime('%Y-%m') else ''
            }

        return monthly_metrics


if __name__ == '__main__':
    # 使用示例
    symbol = 'AAPL'

    analysis = WinnerLoser(symbol)
    monthly_metrics = analysis.winner_loser_effect()
    
    print(f"\n{symbol}最近半年内每月赢家/输家效应:")
    for month, metrics in monthly_metrics.items():
        print(f"\n{month}:")
        print(f"上涨趋势平均持有时间: {metrics['上涨趋势平均持有时间']}")
        print(f"下跌趋势平均持有时间: {metrics['下跌趋势平均持有时间']}")
        print(f"上涨趋势平均交易量: {metrics['上涨趋势平均交易量']}")
        print(f"下跌趋势平均交易量: {metrics['下跌趋势平均交易量']}")
        if metrics['备注']:
            print(f"备注: {metrics['备注']}")
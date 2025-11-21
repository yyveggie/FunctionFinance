from correlation import StockMarketCorrelation
from downside_risk import DownsideRiskCalculator
from inertia_effect import InertiaEffect
from long_term_reversal_effect import LongTermReversalEffect
from momentum_factor import MomentumCalculator
from cumulative_return import CumulativeReturnCalculator
from overtrading import OverTradingAnalysis
from risk_premium import RiskPremium
from skewness_kurtosis import SkewnessKurtosis
from volume_price_correlation import VolumePriceCorrelation
from turnover_rate import TurnoverRatio
from volatility import VolatilityCalculator
from volume_and_price import VolumeChangeCalculator, PriceChangeCalculator
from winner_loser_effect import WinnerLoser
from lsv import LSVMeasure
import pass_the_flower
import prospect_theory
import implied_volatility
import yfinance as yf
import datetime
import pandas as pd
import json
import numpy as np
from datetime import date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

stock = 1
index = 1

# 标准普尔100指数(S&P 100): "^OEX"
# 纳斯达克100指数(NASDAQ-100): "^NDX"
# 纳斯达克综合指数(NASDAQ Composite): "^IXIC"
# 纽约证券交易所综合指数(NYSE Composite): "^NYA"
stock_symbol = 'BABA'
index_symbol = '^SPX' # '^SPX':标普100, '^GSPC': 标普500

x = 0
today = datetime.date.today()
delta = datetime.timedelta(days=x)
today = today - delta
end_date = today.strftime('%Y-%m-%d')

x = 30
delta = datetime.timedelta(days=x)
previous_date = today - delta
start_date = previous_date.strftime('%Y-%m-%d')

stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
market_data = yf.download(index_symbol, start=start_date, end=end_date)

if stock:
    stock_results = {}
    
    print("开始计算个股与市场指数的相关性...")
    # 计算个股收益率与市场指数收益率之间的皮尔逊相关系数,衡量了个股与整个市场的相关性。
    sm = StockMarketCorrelation(stock_symbol, index_symbol, start_date, end_date, stock_data=stock_data, market_data=market_data)
    stock_results['皮尔逊相关系数'] = sm.run()
    print(f"个股 {stock_symbol} 与市场指数 {index_symbol} 的皮尔逊相关系数为: {stock_results['皮尔逊相关系数']}")

    print("开始计算个股的下行风险指标...")
    # 计算个股的下行风险指标  
    dr = DownsideRiskCalculator()
    stock_risk_metrics = dr.calculate_stock_risk(stock_data, market_data)
    stock_results['下行风险指标'] = stock_risk_metrics
    print(f"个股 {stock_symbol} 的下行风险指标为: {stock_results['下行风险指标']}")
    
    print("开始计算个股的隐含波动率指标...")
    iv = implied_volatility.get_monthly_implied_volatility(stock_symbol)
    stock_results['隐含波动率指标'] = iv
    print(f"个股 {stock_symbol} 的隐含波动率指标为: {stock_results['隐含波动率指标']}")
    
    print("开始计算个股过去6个月的涨跌情况...")
    ie = InertiaEffect(stock_data)
    monthly_returns = ie.get_monthly_returns(6)
    stock_results['过去6个月的涨跌情况'] = monthly_returns
    print(f"个股 {stock_symbol} 过去6个月的涨跌情况为: {stock_results['过去6个月的涨跌情况']}")
    
    print("开始计算个股过去3年的涨跌情况...")
    ltr = LongTermReversalEffect()
    yearly_returns = ltr.analyze_stocks(stock_data)
    stock_results['过去3年的涨跌情况'] = yearly_returns
    print(f"个股 {stock_symbol} 过去3年的涨跌情况为: {stock_results['过去3年的涨跌情况']}")
    
    print("开始计算个股的LSV衡量标准值...")
    lsv_measure = LSVMeasure()
    lsv_index = lsv_measure.run_analysis(stock_data)
    stock_results['LSV 衡量标准值'] = lsv_index
    print(f"个股 {stock_symbol} 的LSV衡量标准值为: {stock_results['LSV 衡量标准值']}")
    
    print("开始计算个股的动量因子...")
    end_date_ = datetime.date.today()
    start_date_ = end_date_ - pd.DateOffset(months=6)
    stock_data_ = yf.download(stock_symbol, start=start_date_, end=end_date_)['Adj Close']
    market_data_ = yf.download(index_symbol, start=start_date_, end=end_date_)['Adj Close']
    mo = MomentumCalculator(stock_data_, market_data_)
    momentum_factors = mo.get_monthly_results()
    stock_results['动量因子'] = momentum_factors
    print(f"个股 {stock_symbol} 的动量因子为: {stock_results['动量因子']}")
    
    print("开始计算个股的累计收益率...")  
    cr = CumulativeReturnCalculator(stock_data)
    cumulative_returns = cr.get_results()
    stock_results['累计收益率'] = cumulative_returns
    print(f"个股 {stock_symbol} 的累计收益率为: {stock_results['累计收益率']}")
    
    print("开始计算个股的交易率信息...")
    ot = OverTradingAnalysis(stock_data, market_data)
    overtrading_results = ot.run()
    stock_results['交易率信息'] = overtrading_results
    print(f"个股 {stock_symbol} 的交易率信息为: {stock_results['交易率信息']}")
    
    print("开始分析个股近一个月是否出现博傻...")
    gf = pass_the_flower.greater_fool_theory_analysis(stock_data)
    stock_results['近一个月是否出现博傻'] = gf
    print(f"个股 {stock_symbol} 近一个月是否出现博傻: {stock_results['近一个月是否出现博傻']}")
    
    print("开始计算个股的损失厌恶值...")
    pt = prospect_theory.run(stock_data)
    stock_results['损失厌恶值'] = pt
    print(f"个股 {stock_symbol} 的损失厌恶值为: {stock_results['损失厌恶值']}")
    
    print("开始计算个股的风险溢价值...")
    rp = RiskPremium(stock_symbol, index_symbol)
    stock_risk_premium = rp.calculate_stock_risk_premium()
    stock_results['风险溢价值'] = round(stock_risk_premium, 4)
    print(f"个股 {stock_symbol} 的风险溢价值为: {stock_results['风险溢价值']}")
    
    print("开始计算个股过去一个月的偏度与峰度...")
    sk = SkewnessKurtosis(stock_data)
    skewness, kurt = sk.calculate_skewness_kurtosis()
    stock_results['过去一个月的偏度(Skewness)'] = round(skewness, 4)
    stock_results['过去一个月的峰度(Kurtosis)'] = round(kurt, 4)
    print(f"个股 {stock_symbol} 过去一个月的偏度为: {stock_results['过去一个月的偏度(Skewness)']}")
    print(f"个股 {stock_symbol} 过去一个月的峰度为: {stock_results['过去一个月的峰度(Kurtosis)']}")
    
    print("开始计算个股六个月内交易量与股价的相关性...")
    vp = VolumePriceCorrelation(stock_symbol)  
    vp_result = vp.get_results()
    stock_results['六个月内交易量与股价的相关性'] = vp_result
    print(f"个股 {stock_symbol} 六个月内交易量与股价的相关性为: {stock_results['六个月内交易量与股价的相关性']}")
    
    print("开始计算个股六个月内的换手率...")
    tr = TurnoverRatio(symbol=stock_symbol)
    tr_result = tr.get_results() 
    stock_results['六个月内换手率'] = tr_result
    print(f"个股 {stock_symbol} 六个月内的换手率为: {stock_results['六个月内换手率']}")
    
    print("开始计算个股六个月内股价波动率...")
    vo = VolatilityCalculator(stock_symbol)
    vo_result = vo.calculate_monthly_volatility()
    stock_results['六个月内股价波动率'] = vo_result 
    print(f"个股 {stock_symbol} 六个月内股价波动率为: {stock_results['六个月内股价波动率']}")
    
    print("开始计算个股六个月内交易量变化率...") 
    vc = VolumeChangeCalculator(stock_symbol)
    vc_result = vc.calculate_monthly_volume_changes()
    stock_results['六个月内交易量变化率'] = vc_result
    print(f"个股 {stock_symbol} 六个月内交易量变化率为: {stock_results['六个月内交易量变化率']}")
    
    print("开始计算个股六个月内股价变化率...")  
    pc = PriceChangeCalculator(stock_symbol)
    pc_result = pc.calculate_monthly_price_changes()
    stock_results['六个月内股价变化率'] = pc_result
    print(f"个股 {stock_symbol} 六个月内股价变化率为: {stock_results['六个月内股价变化率']}")
    
    print("开始计算个股今年至今的上涨与下跌平均持有时间及交易量...")
    wl = WinnerLoser(stock_symbol)
    wl_result = wl.winner_loser_effect()
    stock_results['今年至今的上涨与下跌平均持有时间及交易量'] = wl_result
    print(f"个股 {stock_symbol} 今年至今的上涨与下跌平均持有时间及交易量为: {stock_results['今年至今的上涨与下跌平均持有时间及交易量']}")
    
    print('**************************************************************************************************************************')
    print(stock_results)
    print('**************************************************************************************************************************')

    with open(f'{stock_symbol}_results.json', 'w') as f:
        json.dump(stock_results, f, indent=2, cls=CustomJSONEncoder, ensure_ascii=False)

if index:
    index_results = {}
    
    print(f"开始计算市场指数 {index_symbol} 的下行风险指标...")
    # 计算指数的下行风险指标
    downsideRisk = DownsideRiskCalculator()
    stock_risk_metrics = downsideRisk.calculate_market_risk(market_data)
    index_results['下行风险指标'] = stock_risk_metrics
    print(f"市场指数 {index_symbol} 的下行风险指标为: {index_results['下行风险指标']}")
    
    print(f"开始计算市场指数 {index_symbol} 过去6个月的涨跌情况...")
    ie = InertiaEffect(market_data)
    monthly_returns = ie.get_monthly_returns(6)
    index_results['过去6个月的涨跌情况'] = monthly_returns
    print(f"市场指数 {index_symbol} 过去6个月的涨跌情况为: {index_results['过去6个月的涨跌情况']}")
    
    print(f"开始计算市场指数 {index_symbol} 过去3年的涨跌情况...")
    ltr = LongTermReversalEffect()
    yearly_returns = ltr.analyze_stocks(market_data)
    index_results['过去3年的涨跌情况'] = yearly_returns  
    print(f"市场指数 {index_symbol} 过去3年的涨跌情况为: {index_results['过去3年的涨跌情况']}")
    
    print(f"开始计算市场指数 {index_symbol} 的LSV衡量标准值...")
    lsv_measure = LSVMeasure()
    lsv_index = lsv_measure.run_analysis(market_data)
    index_results['LSV 衡量标准值'] = lsv_index
    print(f"市场指数 {index_symbol} 的LSV衡量标准值为: {index_results['LSV 衡量标准值']}")
    
    print(f"开始计算市场指数 {index_symbol} 的累计收益率...")
    cr = CumulativeReturnCalculator(market_data)
    cumulative_returns = cr.get_results()
    index_results['累计收益率'] = cumulative_returns
    print(f"市场指数 {index_symbol} 的累计收益率为: {index_results['累计收益率']}")
    
    print(f"开始分析市场指数 {index_symbol} 近一个月是否出现博傻...")
    gf = pass_the_flower.greater_fool_theory_analysis(market_data)
    index_results['近一个月是否出现博傻'] = gf
    print(f"市场指数 {index_symbol} 近一个月是否出现博傻: {index_results['近一个月是否出现博傻']}")
    
    print(f"开始计算市场指数 {index_symbol} 的损失厌恶值...")
    pt = prospect_theory.run(market_data)
    index_results['损失厌恶值'] = pt
    print(f"市场指数 {index_symbol} 的损失厌恶值为: {index_results['损失厌恶值']}")
    
    print(f"开始计算市场指数 {index_symbol} 的风险溢价值...")  
    rp = RiskPremium(stock_symbol, index_symbol)
    market_risk_premium = rp.calculate_market_risk_premium()
    index_results['风险溢价值'] = round(market_risk_premium, 4)
    print(f"市场指数 {index_symbol} 的风险溢价值为: {index_results['风险溢价值']}")
    
    print(f"开始计算市场指数 {index_symbol} 过去一个月的偏度与峰度...")
    sk = SkewnessKurtosis(market_data)
    skewness, kurt = sk.calculate_skewness_kurtosis()
    index_results['过去一个月的偏度(Skewness)'] = round(skewness, 4)
    index_results['过去一个月的峰度(Kurtosis)'] = round(kurt, 4)
    print(f"市场指数 {index_symbol} 过去一个月的偏度为: {index_results['过去一个月的偏度(Skewness)']}")
    print(f"市场指数 {index_symbol} 过去一个月的峰度为: {index_results['过去一个月的峰度(Kurtosis)']}")
    
    print(f"开始计算市场指数 {index_symbol} 六个月内交易量与股价的相关性...")
    vp = VolumePriceCorrelation(index_symbol)
    vp_result = vp.get_results()
    index_results['六个月内交易量与股价的相关性'] = vp_result
    print(f"市场指数 {index_symbol} 六个月内交易量与股价的相关性为: {index_results['六个月内交易量与股价的相关性']}")
    
    print(f"开始计算市场指数 {index_symbol} 六个月内的换手率...")
    tr = TurnoverRatio(symbol=index_symbol)  
    tr_result = tr.get_results()
    index_results['六个月内换手率'] = tr_result
    print(f"市场指数 {index_symbol} 六个月内的换手率为: {index_results['六个月内换手率']}")
    
    print(f"开始计算市场指数 {index_symbol} 六个月内股价波动率...")
    vo = VolatilityCalculator(index_symbol)
    vo_result = vo.calculate_monthly_volatility()
    index_results['六个月内股价波动率'] = vo_result
    print(f"市场指数 {index_symbol} 六个月内股价波动率为: {index_results['六个月内股价波动率']}")

    print(f"开始计算市场指数 {index_symbol} 六个月内交易量变化率...")
    vc = VolumeChangeCalculator(index_symbol)
    vc_result = vc.calculate_monthly_volume_changes()
    index_results['六个月内交易量变化率'] = vc_result
    print(f"市场指数 {index_symbol} 六个月内交易量变化率为: {index_results['六个月内交易量变化率']}")

    print(f"开始计算市场指数 {index_symbol} 六个月内股价变化率...")
    pc = PriceChangeCalculator(index_symbol)
    pc_result = pc.calculate_monthly_price_changes()
    index_results['六个月内股价变化率'] = pc_result
    print(f"市场指数 {index_symbol} 六个月内股价变化率为: {index_results['六个月内股价变化率']}")

    print(f"开始计算市场指数 {index_symbol} 今年至今的上涨与下跌平均持有时间及交易量...")
    wl = WinnerLoser(index_symbol)
    wl_result = wl.winner_loser_effect()
    index_results['今年至今的上涨与下跌平均持有时间及交易量'] = wl_result
    print(f"市场指数 {index_symbol} 今年至今的上涨与下跌平均持有时间及交易量为: {index_results['今年至今的上涨与下跌平均持有时间及交易量']}")
    
    print('**************************************************************************************************************************')
    print(index_results)
    print('**************************************************************************************************************************')
    
    with open(f'{index_symbol}_results.json', 'w') as f:
        json.dump(index_results, f, indent=2, cls=CustomJSONEncoder, ensure_ascii=False)
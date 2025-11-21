import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveInstitutionalRecommendationPool")
@handle_large_data()
def stock_institute_recommend(symbol="最新投资评级",
                              ) -> pd.DataFrame:
    """
    Get the list of rating information for stocks under different recommendation indicators in institutional recommendations.

    Parameters:
    - symbol (str): The specific indicator to retrieve. It should be one of the following:
                      {'最新投资评级', '上调评级股票', '下调评级股票', '股票综合评级',
                       '首次评级股票', '目标涨幅排名', '机构关注度', '行业关注度', '投资评级选股'}.
    
    Return:
        depending on the specific indicator
    """
    df = ak.stock_institute_recommend(symbol=symbol)
    
    return df


@action(name="RetrieveStockRatingRecords")
@handle_large_data()
def stock_institute_recommend_detail(symbol: str,
        ) -> pd.DataFrame:
    """
    Get the rating information for a specified A-share stock from different rating agencies and analysts.

    Parameters:
    - symbol (str): The ticker symbol of specific stock. e.g. symbol="002709".
    
    Return:
        ['股票代码', '股票名称', '目标价', '最新评级', '评级机构', '分析师', '行业', '评级日期']
    """
    df = ak.stock_institute_recommend_detail(
        symbol=symbol
    )
    
    return df


@action(name="RetrieveInvestmentRating")
@handle_large_data()
def stock_rank_forecast_cninfo(date: str = datetime_utils.yyyymmdd(),
                               ) -> pd.DataFrame:
    """
    Get the rating data from different institutions for a specified stock on a specified date in the A-shares market.

    Parameters:
    - date (str): The specific date with format 'YYYYMMDD'.
    
    Return:
        ['证券代码', '证券简称', '发布日期', '研究机构简称', '研究员名称', '投资评级', '是否首次评级', '评级变化', '前一次投资评级', '目标价格-下限', '目标价格-上限']
    """
    df = ak.stock_rank_forecast_cninfo(date=date)
    
    return df


@action(name="RetrieveStockVote")
@handle_large_data()
def stock_zh_vote_baidu(symbol: str, indicator: str = "股票", ) -> pd.DataFrame:
    """
    Get the voting data on the future price increase or decrease for a specified stock or index in the A-shares market.

    Parameters:
    - symbol: The ticker symbol of the A-share stock or index. e.g. '000001'
    - indicator: The indicator to retrieve, choice of {"指数", "股票"}.
    
    Return:
        ['周期', '看涨', '看跌', '看涨比例', '看跌比例']
    """
    df = ak.stock_zh_vote_baidu(
        symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetProfitForecast_EM")
@handle_large_data()
def stock_profit_forecast_em() -> pd.DataFrame:
    """
    Get future earnings forecast data for all industries in the A-share market.
    
    Return:
        ['代码', '名称', '研报数', '机构投资评级(近六个月)-买入', '机构投资评级(近六个月)-增持', '机构投资评级(近六个月)-中性', '机构投资评级(近六个月)-减持', '机构投资评级(近六个月)-卖出', '2024预测每股收益', '2025预测每股收益', '2026预测每股收益', '2027预测每股收益']
    """
    df = ak.stock_profit_forecast_em()
    
    return df


@action(name="GetHKProfitForecast")
@handle_large_data()
def stock_hk_profit_forecast_et(symbol: str, indicator: str = "评级总览",
                                ) -> pd.DataFrame:
    """
    Get future earnings forecast data from different institutions for a specified stock in the Hong Kong Stock Exchange.

    Parameters:
    - symbol: Ticker symbol of the stock, e.g., "09999".
    - indicator: Indicator for the profit forecast, choose from {"评级总览", "去年度业绩表现", "综合盈利预测", "盈利预测概览"}.
    
    Return:
        ['财政年度', '纯利/亏损', '每股盈利', '每股派息', '证券商', '评级', '目标价', '更新日期']
    """
    df = ak.stock_hk_profit_forecast_et(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetProfitForecast")
@handle_large_data()
def stock_profit_forecast_ths(symbol: str, indicator: str = "预测年报每股收益",
                              ) -> pd.DataFrame:
    """
    Get future performance forecasts by different institutions for a specified A-share stock.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "600519".
    - indicator: Indicator for the profit forecast, choose from {"预测年报每股收益", "预测年报净利润", "业绩预测详表-机构", "业绩预测详表-详细指标预测"}.
    
    Return:
        ['年度', '预测机构数', '最小值', '均值', '最大值', '行业平均数']
    """
    df = ak.stock_profit_forecast_ths(symbol=symbol, indicator=indicator)
    
    return df


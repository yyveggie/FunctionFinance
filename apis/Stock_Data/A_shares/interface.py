import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
from typing import List, Optional, Any
import pandas as pd
import akshare as ak
from crawler import datetime_utils, utils


@action(name="GetDailyWeeklyMonthlyMarketData")
@handle_large_data()
def stock_zh_a_hist(
    symbol: str,
    start_date: str = "19000101",
    end_date: str = datetime_utils.yyyymmdd(),
    adjust: str = "",
    period: str = "daily",
    ) -> pd.DataFrame:
    """
    Get specific A-shares stock historical daily frequency market data.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., '603777'.
    - period: The data frequency. Options are 'daily', 'weekly', 'monthly'.
    - start_date: The start date for the query, in the format 'YYYYMMDD'.
    - end_date: The end date for the query, in the format 'YYYYMMDD'.
    - adjust: Data adjustment type. Empty for no adjustment, 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Returns features:
        ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    """
    return ak.stock_zh_a_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )

@action(name="GetDailyMarketData")
@handle_large_data()
def stock_zh_a_hist_tx(
    symbol: str, 
    start_date: str = "19000101", 
    end_date: str = datetime_utils.yyyymmdd(), 
    adjust: str = "",
    ) -> pd.DataFrame:
    """
    Get specific A-shares stock daily frequency historical market data.

    Parameters:
    - symbol: The ticker symbol of specific stock with market identifier, e.g., 'sz000001' for Shenzhen Stock Exchange.
    - start_date: The start date for the query in 'YYYYMMDD' format.
    - end_date: The end date for the query in 'YYYYMMDD' format.
    - adjust: Data adjustment type. Empty string for no adjustment, 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Returns features:
        ['date', 'open', 'close', 'high', 'low', 'amount']
    """
    return ak.stock_zh_a_hist_tx(
        symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust
    )


@action(name="GetMostRecentMinutelyMarketData")
@handle_large_data()
def stock_zh_a_minute(symbol: str, period: str = "1", adjust: str = "") -> pd.DataFrame:
    """
    Get most recent trading day market data for a specific A-shares stock at minutes frequency.

    Parameters:
    - symbol: The ticker symbol of the stock with market identifier, e.g., 'sh000300' for Shanghai Stock Exchange.
    - period: The frequency of data, options: '1', '5', '15', '30', '60' minutes.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Returns features:
        ['day', 'open', 'high', 'low', 'close', 'volume']
    """
    return ak.stock_zh_a_minute(
        symbol=symbol, period=period, adjust=adjust
    )


@action(name="GetMinutelyMarketData")
@handle_large_data()
def stock_zh_a_hist_min_em(
    symbol: str,
    start_date: str = "1979-09-01 09:32:00",
    end_date: str = datetime_utils.now(),
    period: str = "5",
    adjust: str = "",
    ) -> pd.DataFrame:
    """
    Get historical market data for a specific A-shares stock at minutes frequency.

    Parameters:
    - symbol: The ticker symbol of the stock with market identifier, e.g., 'sh000300' for Shanghai Stock Exchange.
    - start_date: The start date and time for data retrieval, format: 'YYYY-MM-DD HH:MM:SS'.
    - end_date: The end date and time for data retrieval, format: 'YYYY-MM-DD HH:MM:SS'.
    - period: The frequency of data, options: '1', '5', '15', '30', '60' minutes; Note: 1-minute data returns data for the recent 5 trading days and is unadjusted.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted; Note: 1-minute data returns data for the recent 5 trading days and is unadjusted.
    
    Returns features:
        ['时间', '开盘', '收盘', '最高', '最低', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
    """
    return ak.stock_zh_a_hist_min_em(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period=period,
        adjust=adjust,
    )


@action(name="GetIntradayMarketDataLastDay")
@handle_large_data()
def stock_intraday_em(symbol: str) -> pd.DataFrame:                  
    """
    Get the intraday data of the specific A-shares stock for the most recent trading day.

    Parameters:
    - param symbol: The ticker symbol of specific stock, e.g., '000001'.
    
    Returns features:
        ['时间', '成交价', '手数', '买卖盘性质']
    """
    return ak.stock_intraday_em(symbol=symbol)


@action(name="GetIntradayMarketDataSpecificDay")
@handle_large_data()
def stock_intraday_sina(symbol: str, date: str = datetime_utils.yyyymmdd()) -> pd.DataFrame:    
    """
    Get the intraday data for the specific A-shares stock on the specified trading day.

    Parameters:
    - symbol: The ticker symbol of specific stock with market identification, e.g., 'sz000001' for Shenzhen Stock Exchange.
    - date: The trading day for data retrieval, format: 'YYYYMMDD', e.g., '20231108'.
    
    Returns features:
        ['symbol', 'name', 'ticktime', 'price', 'volume', 'prev_price', 'kind']
    """
    return ak.stock_intraday_sina(symbol=symbol, date=date)


@action(name="GetMinutelyMarketData")
@handle_large_data()
def stock_zh_a_hist_pre_min_em(
    symbol: str, 
    start_time: str = "09:00:00", 
    end_time: str = "15:40:00"
    ) -> pd.DataFrame:
    """
    Get market data for a specific A-shares stock at minutes frequency for the most recent trading day.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., '000001'.
    - start_time: The start time for data retrieval, format: 'HH:MM:SS', default: '09:00:00'.
    - end_time: The end time for data retrieval, format: 'HH:MM:SS', default: '15:40:00'.
    
    Returns features:
        ['时间', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '最新价']
    """
    return ak.stock_zh_a_hist_pre_min_em(
        symbol=symbol, start_time=start_time, end_time=end_time
    )


@action(name="GetTickMarketData")
@handle_large_data()
def stock_zh_a_tick_tx(symbol: str) -> pd.DataFrame:
    """
    Get the tick-by-tick transaction data for the specified A-shares stock on the most recent trading day.

    Parameters:
    - symbol: The ticker symbol of specific stock with market identification, e.g., 'sz000001' for Shenzhen Stock Exchange.
    
    Returns features:
        ['成交时间', '成交价格', '价格变动', '成交量', '成交额', '性质']
    """
    return ak.stock_zh_a_tick_tx_js(symbol=symbol)


@action(name="GetBasicStockInfo")
@handle_large_data()
def stock_individual_info_em(symbol: str) -> pd.DataFrame:
    """
    Get detailed basic information for a specific A-shares stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "603777".
    
    Returns features:
        ['item', 'value']
    """
    return ak.stock_individual_info_em(symbol=symbol)


@action(name="GetBidAskData")
@handle_large_data()
def stock_bid_ask_em(symbol: str) -> pd.DataFrame:
    """
    Get the bid and ask data for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "000001".
    
    Returns features list:
        ['item', 'value']
    """
    return ak.stock_bid_ask_em(symbol=symbol)


@action(name="GetASHaresRealTimeData")
@handle_large_data()
def stock_zh_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all A-shares stocks.
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_zh_a_spot_em()


@action(name="GetSSERealTimeData")
@handle_large_data()
def stock_sh_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all stocks listed on the Shanghai Stock Exchange.
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_sh_a_spot_em()


@action(name="GetSZSERealTimeData")
@handle_large_data()
def stock_sz_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all stocks listed on the Shenzhen Stock Exchange.
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_sz_a_spot_em()


@action(name="GetBSERealTimeData")
@handle_large_data()
def stock_bj_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all stocks listed on the Beijing Stock Exchange.
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_bj_a_spot_em()


@action(name="GetNewStockRealTimeData")
@handle_large_data()
def stock_new_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all newly listed A-shares companies.
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '上市时间', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_new_a_spot_em()


@action(name="GetGEMRealTimeData")
@handle_large_data()
def stock_cy_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all companies listed on the Growth Enterprise Market(GEM).
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_cy_a_spot_em()


@action(name="GetSTARMarketRealTimeData")
@handle_large_data()
def stock_kc_a_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all companies listed on the STAR Market (Science and Technology Innovation Board).
    
    Returns features:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_kc_a_spot_em()


@action(name="GetLatestMarketData")
@handle_large_data()
def stock_individual_spot_xq(symbol: str) -> pd.DataFrame:
    """
    Get the latest market data for a specific stock on A-shares or US stocks.

    Parameters:
    - symbol: The ticker symbol of specific stock on A-shares or US stocks.
        Note that it must contain the abbreviation of the securities market. For example: 'SH600000', it represents stock(600000) on the Shanghai Stock Exchange(SH)
    
    Returns features:
        ['item', 'value']
    """
    return ak.stock_individual_spot_xq(symbol=symbol)

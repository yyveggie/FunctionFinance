import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="QuerySecuritiesMarginRatio")
@handle_large_data()
def stock_margin_ratio_pa(date: str = datetime_utils.yyyymmdd(),
                          ) -> pd.DataFrame:
    """
    Get the margin trading data for a specified date in the A-share market.

    Parameters:
    - date: Date of query in the format 'YYYYMMDD'.
    
    Return:
        ['证券代码', '证券简称', '融资比例', '融券比例']
    """
    df = ak.stock_margin_ratio_pa(date=date)
    
    return df


@action(name="GetMarginTradingSummary_SSE")
@handle_large_data()
def stock_margin_sse(
        start_date: str = "19000101", 
        end_date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the summary data of margin trading for the Shanghai Stock Exchange within a specified time range.

    Parameters:
    - start_date: Start date of query in the format 'YYYYMMDD'.
    - end_date: End date of query in the format 'YYYYMMDD'.
    
    Return:
        ['信用交易日期', '融资余额', '融资买入额', '融券余量', '融券余量金额', '融券卖出量', '融资融券余额']
    """
    df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
    
    return df


@action(name="GetMarginTradingDetail_SSE")
@handle_large_data()
def stock_margin_detail_sse(
        date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the detailed margin trading data for all targets on the Shanghai Stock Exchange on a specified date.

    Parameters:
    - date: Date of query in the format 'YYYYMMDD'.
    
    Return:
        ['信用交易日期', '标的证券代码', '标的证券简称', '融资余额', '融资买入额', '融资偿还额', '融券余量', '融券卖出量', '融券偿还量']
    """
    df = ak.stock_margin_detail_sse(date=date)
    
    return df


@action(name="GetMarginTradingSummary_SZSE")
@handle_large_data()
def stock_margin_szse(date: str = datetime_utils.yyyymmdd(),
                      ) -> pd.DataFrame:
    """
    Get the summary data of margin trading for the Shenzhen Stock Exchange within a specified time range.

    Parameters:
    - date: Date of query in the format 'YYYYMMDD'.
    
    Return:
        ['融资买入额', '融资余额', '融券卖出量', '融券余量', '融券余额', '融资融券余额']
    """
    df = ak.stock_margin_szse(date=date)
    
    return df


@action(name="GetMarginTradingDetail_SZSE")
@handle_large_data()
def stock_margin_detail_szse(
        date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get margin trading and short selling detailed data from Shenzhen Stock Exchange.

    Parameters:
    - date: Date of query in the format 'YYYYMMDD'.
    
    Return:
        ['证券代码', '证券简称', '融资买入额', '融资余额', '融券卖出量', '融券余量', '融券余额', '融资融券余额']
    """
    df = ak.stock_margin_detail_szse(date=date)
    
    return df
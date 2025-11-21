import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import akshare as ak
import pandas as pd
from crawler import datetime_utils, utils
from typing import List, Optional, Any


@action(name="GetA-H-SharesList")
@handle_large_data()
def stock_zh_ah_name() -> pd.DataFrame:
    """
    Get the list of all A+H shares listed companies.
    
    Returns features list:
        ['代码', '名称']
    """
    return ak.stock_zh_ah_name()


@action(name="RetrieveA-H-SharesDailyData")
@handle_large_data()
def stock_zh_ah_daily(
        symbol: str, 
        start_year: str = "1900", 
        end_year: str = datetime_utils.year(),
        adjust: str="") -> pd.DataFrame:
    """
    Get all A+H shares stock market data in a specific date range.

    Parameters:
    - symbol: The Hong Kong stock symbol(Hong Kong Stock Exchange), e.g., '02318'.
    - start_year: The start year for data retrieval, e.g., '2000'.
    - end_year: The end year for data retrieval, e.g., '2019'.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Returns features list:
        ['日期','开盘','收盘','最高','最低','成交量']
    """
    return ak.stock_zh_ah_daily(symbol=symbol, start_year=start_year, end_year=end_year, adjust=adjust)


@action(name="GetA-H-SharesSpotData")
@handle_large_data()
def stock_zh_ah_spot() -> pd.DataFrame:
    """
    Get real-time market data for A+H shares stock.
    
    Returns features list:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '买入', '卖出', '成交量', '成交额', '今开', '昨收', '最高', '最低']
    """
    return ak.stock_zh_ah_spot()

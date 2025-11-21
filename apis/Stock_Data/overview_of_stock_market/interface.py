import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetMarketOverviewSSE")
@handle_large_data()
def stock_sse_summary() -> pd.DataFrame:
    """
    Get an overview of stock market information for the most recent trading day from the Shanghai Stock Exchange.
    
    Return:
        ['项目', '股票','科创板','主板']
    """
    df = ak.stock_sse_summary()
    
    return df


@action(name="GetMarketOverviewSZSE")
@handle_large_data()
def stock_szse_summary(date: str = datetime_utils.yyyymmdd(),
                       ) -> pd.DataFrame:
    """
    Get an overview of stock market information for the specific date from the Shenzhen Stock Exchange.

    Parameters:
    - date: The date for which to retrieve market overview data, in the format YYYYMMDD.
    
    Return:
        ['证券类别', '数量','成交金额','总市值','流通市值']
    """
    df = ak.stock_szse_summary(date=date)
    
    return df


@action(name="GetRegionalTradingData")
@handle_large_data()
def stock_szse_area_summary(date: str = datetime_utils.yyyymm(),
                            ) -> pd.DataFrame:
    """
    Get the total trading volume by province in the Shenzhen Stock Exchange on the specified date.

    Parameters:
    - date: The date for which to retrieve the data, in the format YYYYMM.
    
    Return:
        ['序号','地区','总交易额','占市场','股票交易额','基金交易额','债券交易额']
    """
    df = ak.stock_szse_area_summary(date=date)
    
    return df


@action(name="GetStockSectorTransactionData")
@handle_large_data()
def stock_szse_sector_summary(symbol: str, date: str = datetime_utils.yyyymm(),
                              ) -> pd.DataFrame:
    """
    Get an overview of trading data statistics by industry in the Shenzhen Stock Exchange for the specified date.

    Parameters:
    - symbol: The period for the data request, either '当月' for monthly or '当年' for annual data.
    - date: The date for which to retrieve the data, in the format YYYYMM.
    
    Return:
        ['项目名称', '项目名称-英文', '交易天数', '成交金额-人民币元', '成交金额-占总计', '成交股数-股数', '成交股数-占总计', '成交笔数-笔', '成交笔数-占总计']
    """
    df = ak.stock_szse_sector_summary(symbol=symbol, date=date)
    
    return df


@action(name="GetDailyTransactionSummarySSE")
@handle_large_data()
def stock_sse_deal_daily(date: str = datetime_utils.yyyymmdd(),
                         ) -> pd.DataFrame:
    """
    Get the transaction overview data for the Shanghai Stock Exchange on the specified date.

    Parameters:
    - date: The date for which to retrieve the data, in the format YYYYMMDD.
    
    Return:
        ['单日情况', '股票', '主板A', '主板B', '科创板', '股票回购']
    """
    df = ak.stock_sse_deal_daily(date=date)
    
    return df

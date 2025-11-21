import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetRestrictedStockReleaseData")
@handle_large_data()
def stock_restricted_release_queue_sina(symbol: str,
                                        ) -> pd.DataFrame:
    """
    Get the all restricted sale lift data for a specified A-share stock.

    Parameters:
    - symbol: The stock ticker, e.g., "600000".
    
    Return:
        ['代码', '名称', '解禁日期', '解禁数量', '解禁股流通市值', '上市批次', '公告日期']
    """
    df = ak.stock_restricted_release_queue_sina(symbol=symbol)
    
    return df


@action(name="GetRestrictedStockReleaseSummary")
@handle_large_data()
def stock_restricted_release_summary_em(
    symbol: str = "全部股票",
    start_date: str = "19000101",
    end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get restricted sale lift data for a specified market sector within a specified time range.

    Parameters:
    - symbol: The market sector, choice of {"全部股票", "沪市A股", "科创板", "深市A股", "创业板", "京市A股"}.
    - start_date: The start date for the query in the format "YYYYMMDD".
    - end_date: The end date for the query in the format "YYYYMMDD".
    
    Return:
        ['解禁时间', '当日解禁股票家数', '解禁数量', '实际解禁数量', '实际解禁市值', '沪深300指数', '沪深300指数涨跌幅']
    """
    df = ak.stock_restricted_release_summary_em(
        symbol=symbol, start_date=start_date, end_date=end_date
    )
    
    return df


@action(name="GetRestrictedStockReleaseDetail")
@handle_large_data()
def stock_restricted_release_detail_em(
    start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get data on the lifting of share sale restrictions for A-share stocks within a specified period.

    Parameters:
    - start_date: The start date for the query in the format "YYYYMMDD".
    - end_date: The end date for the query in the format "YYYYMMDD".
    
    Return:
        ['序号', '股票代码', '股票简称', '解禁时间', '限售股类型', '解禁数量', '实际解禁数量', '实际解禁市值', '占解禁前流通市值比例', '解禁前一交易日收盘价', '解禁前20日涨跌幅', '解禁后20日涨跌幅']
    """
    df = ak.stock_restricted_release_detail_em(
        start_date=start_date, end_date=end_date
    )
    
    return df


@action(name="GetRestrictedStockReleaseQueue")
@handle_large_data()
def stock_restricted_release_queue_em(symbol: str,
                                      ) -> pd.DataFrame:
    """
    Get the data on the release batches for a specified A-share stock.

    Parameters:
    - symbol: The stock ticker, e.g. '600000'
    
    Return:
        ['解禁时间', '解禁股东数', '解禁数量', '实际解禁数量', '未解禁数量', '实际解禁数量市值', '占总市值比例', '占流通市值比例', '解禁前一交易日收盘价', '限售股类型', '解禁前20日涨跌幅', '解禁后20日涨跌幅']
    """
    df = ak.stock_restricted_release_queue_em(symbol=symbol)
    
    return df
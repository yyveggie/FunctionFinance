import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="Get_B-Shares_Historical_Market_Data")
@handle_large_data()
def stock_zh_b_daily(
        symbol: str,
        start_date: str = "19000101",
        end_date: str = datetime_utils.yyyymmdd(),
        adjust: str = ""
        ) -> pd.DataFrame:
    """
    Get daily historical market data for B-shares specific stock.

    Parameter:
    - symbol: The ticker symbol of specific stock with stock market abbreviation, e.g., 'sh900901' for Shanghai Stock Exchange.
    - start_date: The start date for data retrieval, format: 'YYYYMMDD', e.g., '20201103'.
    - end_date: The end date for data retrieval, format: 'YYYYMMDD', e.g., '20201116'.
    - adjust: Adjustment method. Default is to return unadjusted data.
                   Options: 'qfq' for pre-adjusted data, 'hfq' for post-adjusted data.
    
    Return:
        ['date', 'close', 'high', 'low', 'open', 'volume', 'outstanding_share', 'turnover']
    """
    return ak.stock_zh_b_daily(
        symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust
    )


@action(name="Get_B-Shares_Real-Time_Market_Data")
@handle_large_data()
def stock_zh_b_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all B-shares stocks.
    
    Return:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
    """
    return ak.stock_zh_b_spot_em()


@action(name="Get_B-Shares_Real-Time_Market_Data_2")
@handle_large_data()
def stock_zh_b_spot() -> pd.DataFrame:
    """
    Get real-time market data for all B-shares stocks.
    
    Return:
        ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '买入', '卖出', '昨收', '今开', '最高', '最低', '成交量', '成交额']
    """
    return ak.stock_zh_b_spot()


@action(name="Get_B-Shares_intraday_Market_Data")
@handle_large_data()
def stock_zh_b_minute(
    symbol: str, 
    period: str = "1", 
    adjust: str = ""
    ) -> pd.DataFrame:
    """
    Get the intraday market data for the specified B-shares stock on the most recent trading day.

    Parameter:
    - symbol: The ticker symbol of specific stock with stock market abbreviation, e.g., 'sh900901' with Shanghai Stock Exchange.
    - period: The data frequency to retrieve. Options: '1', '5', '15', '30', '60' minutes. Default is '1'.
    - adjust: Adjustment method for historical data. Default is unadjusted data.
                   Options: 'qfq' for pre-adjusted data, 'hfq' for post-adjusted data.
    
    Return:
        ['day', 'open', 'high', 'low', 'close', 'volume']
    """
    return ak.stock_zh_b_minute(
        symbol=symbol, period=period, adjust=adjust
    )

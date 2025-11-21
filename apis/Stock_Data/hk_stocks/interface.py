import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetHKHistoricalData")
@handle_large_data()
def stock_hk_hist(
    symbol: str,
    period: str = "daily",
    start_date: str = "19700101",
    end_date: str = datetime_utils.yyyymmdd(),
    adjust: str = "",
    ) -> pd.DataFrame:
    """
    Get historical market data for specified Hong Kong Stock Exchange stock.

    Parameters:
    - symbol: The ticker symbol of specific stock in specific tiem range.
    - period: The data period, options: 'daily', 'weekly', 'monthly'.
    - start_date: The start date for data retrieval in YYYYMMDD format.
    - end_date: The end date for data retrieval in YYYYMMDD format.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Return:
        ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    """
    df = ak.stock_hk_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    
    return df


@action(name="GetHKHistoricalDailyData")
@handle_large_data()
def stock_hk_daily(symbol: str, adjust: str = "",
                   ) -> pd.DataFrame:
    """
    Get all historical market data for specified Hong Kong Stock Exchange stock.

    Parameters:
    - symbol: The ticker symbol of specific stock.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted, 'qfq-factor' for pre-adjustment factor, 'hfq-factor' for post-adjustment factor.
    
    Return:
        ['date', 'open', 'high', 'low', 'close', 'volume']
    """
    df = ak.stock_hk_daily(symbol=symbol, adjust=adjust)
    
    return df


@action(name="GetHongKongMainBoardSpotData")
@handle_large_data()
def stock_hk_main_board_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for the Hong Kong Stock Exchange main board. The data is delayed by 15 minutes.
    
    Return:
        ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '今开', '最高', '最低', '昨收', '成交量', '成交额']
    """
    df = ak.stock_hk_main_board_spot_em()
    
    return df


@action(name="GetHongKongStocksSpotData")
@handle_large_data()
def stock_hk_spot_em() -> pd.DataFrame:
    """
    Get real-time market data for all Hong Kong Stock Exchange stocks.
    
    Return:
        ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '今开', '最高', '最低', '昨收', '成交量', '成交额']
    """
    df = ak.stock_hk_spot_em()
    
    return df


@action(name="GetHongKongStocksSpotData2")
@handle_large_data()
def stock_hk_spot() -> pd.DataFrame:
    """
    Get real-time market data for all Hong Kong Stock Exchange stocks. Data is delayed by 15 minutes due to server factors.
    
    Return:
        ['symbol', 'name', 'engname', 'tradetype', 'lasttrade', 'prevclose', 'open', 'high', 'low', 'volume', 'amount', 'ticktime', 'buy', 'sell', 'pricechange', 'changepercent']
    """
    df = ak.stock_hk_spot()
    
    return df


@action(name="RetrieveTimeSharingData")
@handle_large_data()
def stock_hk_hist_min_em(
    symbol: str,
    period: str = "5",
    adjust: str = "",
    start_date: str = "1979-09-01 09:32:00",
    end_date: str = datetime_utils.now(),
    ) -> pd.DataFrame:
    """
    Get intraday data for specified trading days within a specified time range for a stock on the Hong Kong Stock Exchange.

    Parameters:
    - symbol: The ticker symbol of specific Hong Kong stock exchange stock.
    - period: The data period, options: '1', '5', '15', '30', '60'; 1 minute data returns data for the most recent 5 trading days without adjustment.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    - start_date: The start date for data retrieval in YYYY-MM-DD HH:MM:SS format.
    - end_date: The end date for data retrieval in YYYY-MM-DD HH:MM:SS format.
    
    Return:
        ['时间', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '最新价']
    """
    df = ak.stock_hk_hist_min_em(
        symbol=symbol,
        period=period,
        adjust=adjust,
        start_date=start_date,
        end_date=end_date,
    )
    
    return df

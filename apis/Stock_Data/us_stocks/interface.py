import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetFamousUSStocksMarketData")
@handle_large_data()
def stock_us_famous_spot_em(symbol: str,
                            ) -> pd.DataFrame:
    """
    Get real-time quote data for well-known stocks in a specified industry in the U.S. stock market.

    Parameters:
    - symbol: The sector of well-known stocks, options: '科技类', '金融类', '医药食品类', '媒体类', '汽车能源类', '制造零售类'.
    
    Return:
        ['名称', '最新价', '涨跌额', '涨跌幅', '开盘价', '最高价', '最低价', '昨收价', '总市值', '市盈率', '代码']
    """
    df = ak.stock_us_famous_spot_em(symbol=symbol)
    
    return df


@action(name="RetrieveUSHistoricalData")
@handle_large_data()
def stock_us_hist(
    symbol: str,
    period: str = "daily",
    start_date: str = "19000101",
    end_date: str = datetime_utils.yyyymmdd(),
    adjust: str = "",
    ) -> pd.DataFrame:
    """
    Get the quote data for a specified U.S. stock within a specified time range.

    Parameters:
    - symbol: The ticker symbol for the specific U.S. stock.
    - period: The period of data, options: 'daily', 'weekly', 'monthly'.
    - start_date: The start date for data retrieval in YYYYMMDD format.
    - end_date: The end date for data retrieval in YYYYMMDD format.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted.
    
    Return:
        ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    """
    df = ak.stock_us_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    
    return df


@action(name="RetrieveUSHistoricalData2")
@handle_large_data()
def stock_us_daily(symbol: str, adjust: str = "",
                   ) -> pd.DataFrame:
    """
    Get all historical quote data for a specified U.S. stock.

    Parameters:
    - symbol: The ticker symbol for the specific U.S. stock.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted.
    
    Return:
        ['date', 'open', 'high', 'low', 'close', 'volume']
    """
    df = ak.stock_us_daily(symbol=symbol, adjust=adjust)
    
    return df


@action(name="GetPinkSheetMarketSpotData")
@handle_large_data()
def stock_us_pink_spot_em() -> pd.DataFrame:
    """
    Get real-time quote data for the U.S. over-the-counter (OTC) pink sheet market.
    
    Return:
        ['名称', '最新价', '涨跌额', '涨跌幅', '开盘价', '最高价', '最低价', '昨收价', '总市值', '市盈率', '代码']
    """
    df = ak.stock_us_pink_spot_em()
    
    return df


@action(name="GetUSStocksSpotData")
@handle_large_data()
def stock_us_spot_em() -> pd.DataFrame:
    """
    Get real-time quote data for all U.S. stocks.
    
    Return:
        ['名称', '最新价', '涨跌额', '涨跌幅', '开盘价', '最高价', '最低价', '昨收价', '总市值', '市盈率', '成交量', '成交额', '振幅', '换手率', '代码']
    """
    df = ak.stock_us_spot_em()
    
    return df


@action(name="RetrieveTimeSharingData")
@handle_large_data()
def stock_us_hist_min_em(
    symbol: str,
    start_date: str = "1979-09-01 09:32:00",
    end_date: str = "2222-01-01 09:32:00",
    ) -> pd.DataFrame:
    """
    Get intraday data for a specified U.S. stock within a specified time range.

    Parameters:
    - symbol: The ticker symbol for the specific U.S. stock.
    - start_date: The start date for data retrieval in YYYY-MM-DD HH:MM:SS format.
    - end_date: The end date for data retrieval in YYYY-MM-DD HH:MM:SS format.
    
    Return:
        ['时间', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '最新价']
    """
    df = ak.stock_us_hist_min_em(
        symbol=symbol, start_date=start_date, end_date=end_date
    )
    
    return df

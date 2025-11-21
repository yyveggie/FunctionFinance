import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from crawler import datetime_utils, utils


@action(name="GetDividendDistributionData")
@handle_large_data()
def news_trade_notify_dividend_baidu(date: str = datetime_utils.yyyymmdd(),
                                     ) -> pd.DataFrame:
    """
    Get the dividend distribution data for Hong Kong Stock Exchange stocks on the specified date.

    Parameters:
    - date: The date in the format "YYYYMMDD", e.g., "20220916".
    
    Return:
        ['股票代码', '除权日', '分红', '送股', '转增', '实物', '交易所', '股票简称', '报告期']
    """
    return ak.news_trade_notify_dividend_baidu(date=date)


@action(name="GetDividendDistribution")
@handle_large_data()
def stock_fhps_em(date: str = datetime_utils.yyyymmdd(),
                  ) -> pd.DataFrame:
    """
    Get the dividend distribution data for A-shares on the specified date.

    Parameters:
    - date: Date specifying the dividend distribution data to retrieve. Choice of {"XXXX0630", "XXXX1231"}; indicating {"June 30", "December 31"}. Starting from "19901231".
    
    Return:
        ['代码', '名称', '送转股份-送转总比例', '送转股份-送转比例', '送转股份-转股比例', '现金分红-现金分红比例', '现金分红-股息率', '每股收益', '每股净资产', '每股公积金', '每股未分配利润', '净利润同比增长', '总股本', '预案公告日', '股权登记日', '除权除息日', '方案进度', '最新公告日期']
    """
    return ak.stock_fhps_em(date=date)


@action(name="GetDividendDistributionDetail")
@handle_large_data()
def stock_fhps_detail_em(symbol: str,
                         ) -> pd.DataFrame:
    """
    Get the dividend distribution data for A-shares specific stock on the specified date.

    Parameters:
    - symbol: Ticker symbol of the specific stock.
    
    Return:
        ['报告期', '业绩披露日期', '送转股份-送转总比例', '送转股份-送股比例', '送转股份-转股比例', '现金分红-现金分红比例', '现金分红-现金分红比例描述', '现金分红-股息率', '每股收益', '每股净资产', '每股公积金', '每股未分配利润', '净利润同比增长', '总股本', '预案公告日', '股权登记日', '除权除息日', '方案进度', '最新公告日期']
    """
    return ak.stock_fhps_detail_em(symbol=symbol)


@action(name="GetDividendFinancingDetail")
@handle_large_data()
def stock_fhps_detail_ths(symbol: str,
                          ) -> pd.DataFrame:
    """
    Get the dividend financing data for the specified A-share stock.

    Parameters:
    - symbol: Ticker symbol of the specific stock.
    
    Return:
        ['报告期', '董事会日期', '股东大会预案公告日期', '实施公告日', '分红方案说明', 'A股股权登记日', 'A股除权除息日', '分红总额', '方案进度', '股利支付率', '税前分红率']
    """
    return ak.stock_fhps_detail_ths(symbol=symbol)


@action(name="GetHongKongDividendDistributionDetail")
@handle_large_data()
def stock_hk_fhpx_detail_ths(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get the all dividend distribution data for Hong Kong Stock Exchange specific stock.

    Parameters:
    - symbol: Ticker symbol of the specific stock.
    
    Return:
        ['公告日期', '方案', '除净日', '派息日', '过户日期起止日-起始', '过户日期起止日-截止', '类型', '进度', '以股代息']
    """
    return ak.stock_hk_fhpx_detail_ths(symbol=symbol)


@action(name="GetHistoricalDividend")
@handle_large_data()
def stock_history_dividend() -> pd.DataFrame:
    """
    Get the historical dividend data for all A-shares stocks.
    
    Return:
        ['代码', '名称', '上市日期', '累计股息', '年均股息', '分红次数', '融资总额', '融资次数']
    """
    return ak.stock_history_dividend()

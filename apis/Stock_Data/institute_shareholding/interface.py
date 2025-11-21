import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveInstitutionalShareholding")
@handle_large_data()
def stock_institute_hold(symbol: str = datetime_utils.yyyyq(),
                         ) -> pd.DataFrame:
    """
    Get data on changes in institutional holdings for all A-share stocks.

    Parameters:
    - symbol (str): The symbol indicating the financial report period.
                      It should be in the format "YYYYQ", where YYYY represents the year
                      and Q represents the quarter. For example, "20201" represents the
                      first quarter of 2020.
    
    Return:
        ['证券代码', '证券简称', '机构数', '机构数变化', '持股比例', '持股比例增幅', '占流通股比例', '占流通股比例增幅']
    """
    df = ak.stock_institute_hold(symbol=symbol)
    
    return df


@action(name="RetrieveInstitutionalShareholdingDetail")
@handle_large_data()
def stock_institute_hold_detail(stock: str, quarter: str = datetime_utils.yyyyq(),
                                ) -> pd.DataFrame:
    """
    Get data on changes in institutional holdings for specific A-share stock.

    Parameters:
    - stock (str): The ticker symbol of specific stock in A-Shares.
    - quarter (str): The financial report period.
                       It should be in the format "YYYYQ", where YYYY represents the year
                       and Q represents the quarter. For example, "20201" represents the
                       first quarter of 2020.
    
    Return:
        ['持股机构类型', '持股机构代码', '持股机构简称', '持股机构全称', '持股数', '最新持股数', '持股比例', '最新持股比例', '占流通股比例', '最新占流通股比例', '持股比例增幅', '占流通股比例增幅']
    """
    df = ak.stock_institute_hold_detail(
        stock=stock, quarter=quarter
    )
    
    return df


@action(name="GetInstitutionalDailyStatistics")
@handle_large_data()
def stock_lhb_jgmmtj_em(
    start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get daily statistics of institutional buying and selling in the A-share market within a specified time range.

    Parameters:
    - start_date: The start date of the time range. The form is 'YYYYMMDD'
    - end_date: The end date of the time range. The form is 'YYYYMMDD'

    Return:
        ['代码', '名称', '收盘价', '涨跌幅', '买方机构数', '卖方机构数', '机构买入总额', '机构卖出总额', '机构买入净额', '市场总成交额', '机构净买额占总成交额比', '换手率', '流通市值', '上榜原因', '上榜日期']
    """
    df = ak.stock_lhb_jgmmtj_em(
        start_date=start_date, end_date=end_date
    )
    
    return df


@action(name="GetInstitutionalDailyStatistics")
@handle_large_data()
def stock_lhb_jgstatistic_em(symbol: str = "近三月",
                             ) -> pd.DataFrame:
    """
    Get institutional buying and selling information data for stocks on the Dragon and Tiger list within a specified time range.

    Parameters:
    - symbol: option of time range, choice of {"近一月", "近三月", "近六月", "近一年"}.
    
    Return:
        ['代码', '名称', '收盘价', '涨跌幅', '龙虎榜成交金额', '上榜次数', '机构买入额', '机构买入次数', '机构卖出额', '机构卖出次数', '机构净买额', '近1个月涨跌幅', '近3个月涨跌幅', '近6个月涨跌幅', '近1年涨跌幅']
    """
    df = ak.stock_lhb_jgstatistic_em(symbol=symbol)
    
    return df

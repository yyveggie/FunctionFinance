import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetSuspendResumeData")
@handle_large_data()
def news_trade_notify_suspend_baidu(date: str = datetime_utils.yyyymmdd(),
                                    ) -> pd.DataFrame:
    """
    Get suspension and resumption data for a specified date from the Hong Kong Stock Exchange.

    Parameters:
    - date: The date in the format "YYYYMMDD", e.g., "20220513".
    
    Return:
        ['股票代码', '股票简称', '交易所', '停牌时间', '复牌时间', '停牌事项说明']
    """
    df = ak.news_trade_notify_suspend_baidu(date=date)
    
    return df


@action(name="RetrieveSZDelistedStocks")
@handle_large_data()
def stock_info_sz_delist(symbol="终止上市公司",
                         ) -> pd.DataFrame:
    """
    Get data on stocks delisted/suspended from the Shenzhen Stock Exchange.

    Parameters:
    - symbol (str, optional): Specifies whether to retrieve delisted or suspended stocks. Defaults to "终止上市公司".
            Choices are {"暂停上市公司", "终止上市公司"}.
    
    Return:
        ['证券代码', '证券简称', '上市日期', '终止上市日期']
    """
    df = ak.stock_info_sz_delist(symbol=symbol)
    
    return df


@action(name="RetrieveSTAndQNetStopStocks")
@handle_large_data()
def stock_staq_net_stop() -> pd.DataFrame:
    """
    Get data for all stocks delisted and in the special treatment (ST) category.
    
    Return:
        ['序号', '代码', '名称']
    """
    df = ak.stock_staq_net_stop()
    
    return df


@action(name="RetrieveShanghaiDelistedStocks")
@handle_large_data()
def stock_info_sh_delist() -> pd.DataFrame:
    """
    Get data on stocks suspended/delisted from the Shanghai Stock Exchange.
    
    Return:
        ['公司代码', '公司简称', '上市日期', '暂停上市日期']
    """
    df = ak.stock_info_sh_delist()
    
    return df

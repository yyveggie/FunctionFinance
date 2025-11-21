import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetLimitUpStocks")
@handle_large_data()
def stock_zt_pool_em(date: str = datetime_utils.yyyymmdd(),
                     ) -> pd.DataFrame:
    """
    Get market data of stocks that hit the limit up for the specified date.

    Parameters:
    - date: The date, format 'YYYYMMDD' e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '成交额', '流通市值', '总市值', '换手率', '封板资金', '首次封板时间', '最后封板时间', '炸板次数', '涨停统计', '连板数', '所属行业']
    """
    return ak.stock_zt_pool_em(date=date)


@action(name="GetPreviousLimitUpStocks")
@handle_large_data()
def stock_zt_pool_previous_em(
        date: str=datetime_utils.yyyymmdd()) -> pd.DataFrame:
    """
    Get the data for the stock pool that hit the daily limit the day before a specified date in the A-share market.

    Parameters:
    - date: The date, format 'YYYYMMDD', e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '涨停价', '成交额', '流通市值', '总市值', '换手率', '涨速', '振幅', '昨日封板时间', '昨日连板数', '涨停统计', '所属行业']
    """
    return ak.stock_zt_pool_previous_em(date=date)


@action(name="GetStrongStocks")
@handle_large_data()
def stock_zt_pool_strong_em(
        date: str=datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the data for the strong stock pool on a specified date in the A-share market.

    Parameters:
    - date: The date, format 'YYYYMMDD', e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '涨停价', '成交额', '流通市值', '总市值', '换手率', '涨速', '是否新高', '量比', '涨停统计', '入选理由', '所属行业']
    """
    df = ak.stock_zt_pool_strong_em(date=date)
    
    return df


@action(name="GetSubNewStocksUnderLimitUp")
@handle_large_data()
def stock_zt_pool_sub_new_em(
        date: str=datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the data for the sub-new stock pool on a specified date in the A-share market.

    Parameters:
    - date: The date, format 'YYYYMMDD', e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '涨停价', '成交额', '流通市值', '总市值', '转手率', '开板几日', '开板日期', '上市日期', '是否新高', '涨停统计', '所属行业']
    """
    df = ak.stock_zt_pool_sub_new_em(date=date)
    
    return df


@action(name="GetFailedToLimitUpStocks")
@handle_large_data()
def stock_zt_pool_zbgc_em(
        date: str=datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the data for the burst limit stock pool on a specified date in the A-share market.

    Parameters:
    - date: The date, format 'YYYYMMDD', e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '涨停价', '成交额', '流通市值', '总市值', '换手率', '涨速', '首次封板时间', '炸板次数', '涨停统计', '振幅', '所属行业']
    """
    df = ak.stock_zt_pool_zbgc_em(date=date)
    
    return df


@action(name="GetLimitDownStocksPool")
@handle_large_data()
def stock_zt_pool_dtgc_em(date: str = datetime_utils.yyyymmdd(),
                          ) -> pd.DataFrame:
    """
    Get the recent data for the stock pool that hit the daily limit down on a specified date in the A-share market.

    Parameters:
    - date: The date, format 'YYYYMMDD', e.g., '20231129'.
    
    Return:
        ['代码', '名称', '涨跌幅', '最新价', '成交额', '流通市值', '总市值', '动态市盈率', '换手率', '封单资金', '最后封板时间', '板上成交额', '连续跌停', '开板次数', '所属行业']
    """
    df = ak.stock_zt_pool_dtgc_em(date=date)
    
    return df


@action(name="GetMarketActivityAnalysis")
@handle_large_data()
def stock_market_activity_legu() -> pd.DataFrame:
    """
    Get current money-making effect analysis data.
    
    Return:
        ['item', 'value']
    """
    df = ak.stock_market_activity_legu()
    
    return df

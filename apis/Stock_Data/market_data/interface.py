import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveSectorSpot")
@handle_large_data()
def stock_sector_spot(indicator: str="新浪行业") -> pd.DataFrame:
    """
    Get real-time market data for a specified industry in the A-share market.

    Parameters:
    - indicator (str): The industry indicator, choice of {"新浪行业", "启明星行业", "概念", "地域", "行业"}.
    
    Return:
        ['label', '板块', '公司家数', '平均价格', '涨跌额', '涨跌幅', '总成交量', '总成交额', '股票代码', '个股-涨跌幅', '个股-当前价', '个股-涨跌额', '股票名称']
    """
    return ak.stock_sector_spot(indicator=indicator)


@action(name="DailyDragonTigerListDetails")
@handle_large_data()
def stock_lhb_detail_daily_sina(date: str=datetime_utils.yyyymmdd()) -> pd.DataFrame:
    """
    Get the market data for the Dragon and Tiger list on a specified date.

    Parameters:
    - date: The trading date in the format "YYYYMMDD".
    
    Return:
        ['序号', '股票代码', '股票名称', '收盘价', '对应值', '成交量', '成交额', '指标']
    """
    return ak.stock_lhb_detail_daily_sina(date=date)


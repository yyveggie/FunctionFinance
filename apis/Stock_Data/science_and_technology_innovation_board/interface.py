import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveKechuangBoardDailyData")
@handle_large_data()
def stock_zh_kcb_daily(symbol: str, adjust: str = "",
                       ) -> pd.DataFrame:
    """
    Get historical market data for a specified stock on the A-share STAR Market.

    Parameters:
    - symbol: The stock symbol with market identifier, e.g., 'sh688008'.
    - adjust: Adjust the data, options: '', 'qfq' for pre-adjusted, 'hfq' for post-adjusted, 'hfq-factor' for pre-adjusted factor, 'hfq-factor' for post-adjusted factor.
    
    Return:
        ['date', 'close', 'high', 'low', 'open', 'volume', 'after_volume', 'after_amount', 'outstanding_share', 'turnover']
    """
    return ak.stock_zh_kcb_daily(symbol=symbol, adjust=adjust)


@action(name="GetKechuangBoardSpotData")
@handle_large_data()
def stock_zh_kcb_spot() -> pd.DataFrame:
    """
    Get real-time market data for all companies listed on the A-shares KeChuang/STAR Market.
    
    Return:
        ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '买入', '卖出', '昨收', '今开', '最高', '最低', '成交量', '成交额', '时点', '市盈率', '市净率', '流通市值', '总市值', '换手率']
    """
    return ak.stock_zh_kcb_spot()

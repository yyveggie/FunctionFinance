import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import pandas as pd
import akshare as ak


@action(name="GetDelistedStocksMarketData")
@handle_large_data()
def stock_zh_a_stop_em() -> pd.DataFrame:
    """
    Get market data on stocks that are delisted of most recent trading day.
    
    Return:
        ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率']
    """
    return ak.stock_zh_a_stop_em()

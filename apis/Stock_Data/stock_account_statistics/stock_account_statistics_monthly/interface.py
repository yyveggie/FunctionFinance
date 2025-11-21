import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveStockAccountStatistics")
@handle_large_data()
def stock_account_statistics_em() -> pd.DataFrame:
    """
    Get statistical data of A-share stock accounts.
    
    Return:
        ['数据日期', '新增投资者-数量', '新增投资者-环比', '新增投资者-同比', '期末投资者-总量', '期末投资者-A股账户', '期末投资者-B股账户', '沪深总市值', '沪深户均市值', '上证指数-收盘', '上证指数-涨跌幅']
    """
    return ak.stock_account_statistics_em()

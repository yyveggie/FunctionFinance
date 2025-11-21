import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetIPOMarketData")
@handle_large_data()
def stock_ipo_benefit_ths() -> pd.DataFrame:
    """
    Get all market data for the most recent trading day of A-share new stocks that benefited from new IPOs.
    
    Return:
        ['股票代码', '股票简称', '收盘价', '涨跌幅', '市值', '参股家数', '投资总额', '投资占市值比', '参股对象']
    """
    return ak.stock_ipo_benefit_ths()

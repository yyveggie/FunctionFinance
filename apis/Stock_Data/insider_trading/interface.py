import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetInsiderTrading")
@handle_large_data()
def stock_inner_trade_xq() -> pd.DataFrame:
    """
    Get all historical data of insider trading in A-shares.
    
    Return:
        ['股票代码', '股票名称', '变动日期', '变动人', '变动股数', '成交均价', '变动后持股数', '与董监高关系', '董监高职务']
    """
    return ak.stock_inner_trade_xq()

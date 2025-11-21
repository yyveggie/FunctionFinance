import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetMarketDataForSubNewStock")
@handle_large_data()
def stock_zh_a_new() -> pd.DataFrame:
    """
    Get the most recent trading day quote data for all newly listed A-share stocks.
    
    Return:
        ['symbol', 'code', 'name', 'open', 'high', 'low', 'volume', 'amount', 'mktcap', 'turnoverratio']
    """
    return ak.stock_zh_a_new()

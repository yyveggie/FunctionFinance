import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import pandas as pd
import akshare as ak


@action(name="GetConceptSectorDailyKLineAndChipDistribution")
@handle_large_data()
def stock_cyq_em(symbol: str, adjust: str = "") -> pd.DataFrame:
    """
    Get the chip distribution data for the specified A-shares stock over the last 90 trading days.

    Parameter:
    - symbol: The ticker stock of specific stock, e.g., "000001".
    - adjust: The adjustment method for price data, choices are "qfq" for pre-adjustment, "hfq" for post-adjustment, and "" for no adjustment.
    
    Return:
        ['日期', '获利比例', '平均成本', '90成本-低', '90成本-高', '90集中度', '70成本-低', '70成本-高', '70集中度']
    """
    return ak.stock_cyq_em(symbol=symbol, adjust=adjust)
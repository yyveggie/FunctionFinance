import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetESGRatingData")
@handle_large_data()
def stock_esg_rate_sina() -> pd.DataFrame:
    """
    Get all data of ESG rating for all stocks listed in Mainland China and Hong Kong.
    
    Return:
        ['成分股代码', '评级机构', '评级', '评级季度', '标识', '交易市场']
    """
    return ak.stock_esg_rate_sina()


@action(name="GetHuazhengIndexData")
@handle_large_data()
def stock_esg_hz_sina() -> pd.DataFrame:
    """
    Get all data of Huazheng index for all A-Shares stocks.
    
    Return:
        ['日期', '股票代码', '交易市场', '股票名称', 'ESG评分', 'ESG等级', '环境', '环境等级', '社会', '社会等级', '公司治理', '公司治理等级']
    """
    return ak.stock_esg_hz_sina()

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import akshare as ak
import pandas as pd
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveAnalystRankData")
@handle_large_data()
def stock_analyst_rank_em(year: str = datetime_utils.year()) -> pd.DataFrame:
    """
    Get the evaluation index data of all stock analysts for the specific year.

    Parameters:
    - year: The year for which to retrieve data. It should be a string in the format 'YYYY'.
    
    Returns features:
        ['分析师名称', '分析师单位', '年度指数', 'xxxx年收益率', '3个月收益率', '6个月收益率', '12个月收益率', '成分股个数', 'xxxx最新个股评级-股票名称', 'xxxx最新个股评级-股票代码', '分析师ID', '行业代码', '行业', '更新日期', '年度']
    """
    return ak.stock_analyst_rank_em(year=year)

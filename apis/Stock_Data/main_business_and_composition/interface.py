import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetMainBusinessIntroduction")
@handle_large_data()
def stock_zyjs_ths(symbol: str) -> pd.DataFrame:
    """
    Get the main business introduction data for a specified stock.

    Parameters:
    - symbol: The stock symbol for the company, e.g. symbol="000066"
    
    Return:
        ['股票代码','主营业务','产品类型','产品名称','经营范围']
    """
    return ak.stock_zyjs_ths(symbol=symbol)


@action(name="GetMainBusinessComposition")
@handle_large_data()
def stock_zygc_em(symbol: str) -> pd.DataFrame:
    """
    Get the main business composition data for a specified stock.

    Parameters:
    - symbol: The stock ticker with stock market abbreviation, e.g., "SH688041" for Shanghai Stock Exchange.
    
    Return:
        ['股票代码', '报告日期', '分类类型', '主营构成', '主营收入', '收入比例', '主营成本', '成本比例', '主营利润', '利润比例', '毛利率']
    """
    return ak.stock_zygc_em(symbol=symbol)


@action(name="GetMainBusinessComposition2")
@handle_large_data()
def stock_zygc_ym(symbol: str) -> pd.DataFrame:
    """
    Get the main business composition data for a specified stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "000001"
    
    Return:
        ['报告期', '分类方向', '分类', '营业收入', '营业收入-同比增长', '营业收入-占主营收入比', '营业成本', '营业成本-同比增长', '营业成本-占主营成本比', '毛利率', '毛利率-同比增长']
    """
    return ak.stock_zygc_ym(symbol=symbol)

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetHistoricalRatings")
@handle_large_data()
def stock_comment_detail_zhpj_lspf_em(symbol: str,
                                      ) -> pd.DataFrame:
    """
    Get historical ratings and grades for a specified A-share stock (from Thousand Stocks Thousand Reviews).

    Parameters:
    - symbol: The stock symbol, e.g., "600000".
    
    Return:
        ['日期', '评分', '股价']
    """
    return ak.stock_comment_detail_zhpj_lspf_em(symbol=symbol) 


@action(name="RetrieveStockCommentDetail")
@handle_large_data()
def stock_comment_detail_zlkp_jgcyd_em(symbol: str,
                                       ) -> pd.DataFrame:
    """
    Get historical institutional participation values for a specified A-share stock.

    Parameters:
    - symbol (str): The ticker symbol of specific stock.
    
    Return:
        ['date', 'value']
    """
    return ak.stock_comment_detail_zlkp_jgcyd_em(
        symbol=symbol
    )


@action(name="GetUserAttentionIndex")
@handle_large_data()
def stock_comment_detail_scrd_focus_em(symbol: str,
                                       ) -> pd.DataFrame:
    """
    Get historical user attention index data for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "600000".
    
    Return:
        ['日期', '用户关注指数', '收盘价']
    """
    return ak.stock_comment_detail_scrd_focus_em(symbol=symbol)


@action(name="GetMarketParticipationDesire")
@handle_large_data()
def stock_comment_detail_scrd_desire_em(symbol: str,
                                        ) -> pd.DataFrame:
    """
    Get the market participation willingness value for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "600000".
    
    Return:
        ['日期时间', '大户', '全部', '散户']
    """
    return ak.stock_comment_detail_scrd_desire_em(symbol=symbol)


@action(name="GetDailyMarketParticipationDesire")
@handle_large_data()
def stock_comment_detail_scrd_desire_daily_em(symbol: str,
                                              ) -> pd.DataFrame:
    """
    Get the daily willingness change value for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "600000".
    
    Return:
        ['日期','当日意愿下降','五日累计意愿']
    """
    return ak.stock_comment_detail_scrd_desire_daily_em(symbol=symbol)


@action(name="GetMarketCost")
@handle_large_data()
def stock_comment_detail_scrd_cost_em(symbol: str,
                                      ) -> pd.DataFrame:
    """
    Get the daily market cost for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock, e.g., "600000".
    
    Return:
        ['日期','市场成本','5日市场成本']
    """
    return ak.stock_comment_detail_scrd_cost_em(symbol=symbol)


@action(name="RetrieveStockComments")
@handle_large_data()
def stock_comment_em() -> pd.DataFrame:
    """
    Get the latest rating data for all A-share stocks (from Thousand Stocks Thousand Reviews).
    
    Return:
        ['代码', '名称', '最新价', '涨跌幅', '换手率', '市盈率', '主力成本', '机构参与度', '综合得分', '上升', '目前排名', '关注指数', '交易日']
    """
    return ak.stock_comment_em()

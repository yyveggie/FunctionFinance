import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetMarketDataOfNewStock")
@handle_large_data()
def stock_zh_a_new_em() -> pd.DataFrame:
    """
    Get the market data for all stocks in the new stock sector for the current trading day.
    
    Return:
        ['序号', '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率']
    """
    df = ak.stock_zh_a_new_em()
    
    return df


@action(name="GetNewStockPerformance")
@handle_large_data()
def stock_dxsyl_em(
        ) -> pd.DataFrame:
    """
    Get all data on the return rates from initial public offerings (IPOs).
    
    Return:
        ['股票代码', '股票简称', '发行价', '最新价', '网上发行中签率', '网上有效申购股数', '网上有效申购户数', '网上超额认购倍数', '网下配售中签率', '网下有效申购股数', '网下有效申购户数', '网下配售认购倍数', '总发行数量', '开盘溢价', '首日涨幅', '上市日期']
    """
    df = ak.stock_dxsyl_em()
    
    return df


@action(name="GetNewStockSubscriptionAndLottery")
@handle_large_data()
def stock_xgsglb_em(symbol: str = "全部股票",
                    ) -> pd.DataFrame:
    """
    Get data on new stock subscriptions and allotment inquiries for a specified market.

    Parameters:
    - symbol: The stock market, e.g., "全部股票", "沪市主板", "科创板", "深市主板", "创业板", "北交所".
    
    Return:
        ['股票代码', '股票简称', '申购代码', '发行总数', '网上发行', '顶格申购需配市值', '申购上限', '发行价格', '最新价', '首日收盘价', '申购日期', '中签号公布日', '中签缴款日期', '上市日期', '发行市盈率', '行业市盈率', '中签率', '询价累计报价倍数', '配售对象报价家数', '连续一字板数量', '涨幅', '每中一签获利']
    """
    df = ak.stock_xgsglb_em(symbol=symbol)
    
    return df


@action(name="GetNewStockIPOInfo")
@handle_large_data()
def stock_ipo_info(stock: str,
                   ) -> pd.DataFrame:
    """
    Get basic information data on new stock issues in the A-share market.

    Parameters:
    - stock: The new stock ticker, e.g., "600004".
    
    Return:
        ['item', 'value']
    """
    df = ak.stock_ipo_info(stock=stock)
    
    return df


@action(name="RetrieveNewIPOData")
@handle_large_data()
def stock_new_ipo_cninfo() -> pd.DataFrame:
    """
    Get data on all new stock issues in the A-share market in recent 3 years.
    
    Return:
        ['证劵代码', '证券简称', '上市日期', '申购日期', '发行价', '总发行数量', '发行市盈率', '上网发行中签率', '摇号结果公告日', '中签公告日', '中签缴款日', '网上申购上限', '上网发行数量']
    """
    df = ak.stock_new_ipo_cninfo()
    
    return df

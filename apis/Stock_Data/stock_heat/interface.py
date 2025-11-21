import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetHotStocks")
@handle_large_data()
def stock_hot_follow_xq(symbol: str = "最热门",
                        ) -> pd.DataFrame:
    """
    Get A-Shares stocks attention ranking data.

    Parameters:
    - symbol: The symbol of the hot stocks, either "本周新增" or "最热门".
    
    Return:
        ['股票代码', '股票简称', '关注', '最新价']
    """
    df = ak.stock_hot_follow_xq(symbol=symbol)
    
    return df


@action(name="GetDiscussionRanking")
@handle_large_data()
def stock_hot_tweet_xq(symbol: str = "最热门",
                       ) -> pd.DataFrame:
    """
    Get A-Shares stocks discussion ranking data.

    Parameters:
    - symbol: The symbol of the hot stocks, either "本周新增" or "最热门".
    
    Return:
        ['股票代码', '股票简称', '关注', '最新价']
    """
    df = ak.stock_hot_tweet_xq(symbol=symbol)
    
    return df


@action(name="GetTradingRanking")
@handle_large_data()
def stock_hot_deal_xq(symbol: str = "最热门",
                      ) -> pd.DataFrame:
    """
    Get A-shares trading ranking data.

    Parameters:
    - symbol: The symbol of the hot stocks, either "本周新增" or "最热门".
    
    Return:
        ['股票代码', '股票简称', '关注', '最新价']
    """
    df = ak.stock_hot_deal_xq(symbol=symbol)
    
    return df


@action(name="GetHotStockRanking")
@handle_large_data()
def stock_hot_rank_wc(date: str = datetime_utils.yyyymmdd(),
                      ) -> pd.DataFrame:
    """
    Get the popularity ranking data of A-share stocks for a specified date.

    Parameters:
    - date: The date of the ranking data in the format "YYYYMMDD".
    
    Return:
        ['股票代码', '股票简称', '现价', '涨跌幅', '个股热度', '个股热度排名', '排名日期']
    """
    df = ak.stock_hot_rank_wc(date=date)
    
    return df


@action(name="GetPopularityRanking")
@handle_large_data()
def stock_hot_rank_em() -> pd.DataFrame:
    """
    Get the popularity ranking data for the top 100 A-shares stocks for the current trading day.
    
    Return:
        ['当前排名', '代码', '股票名称', '最新价', '涨跌额', '涨跌幅']
    """
    df = ak.stock_hot_rank_em()
    
    return df


@action(name="GetSurgeRanking")
@handle_large_data()
def stock_hot_up_em() -> pd.DataFrame:
    """
    Get the surge ranking data of the top 100 A-shares stocks before the current trading day.
    
    Return:
        ['排名较昨日变动', '当前排名', '代码', '股票名称', '最新价', '涨跌额', '涨跌幅']
    """
    df = ak.stock_hot_up_em()
    
    return df


@action(name="GetPopularityRankingHK")
@handle_large_data()
def stock_hk_hot_rank_em() -> pd.DataFrame:
    """
    Get the popularity ranking data of the top 100 stocks on the Hong Kong Stock Exchange before the current trading day.
    
    Return:
        ['当前排名', '代码', '股票名称', '最新价', '涨跌幅']
    """
    df = ak.stock_hk_hot_rank_em()
    
    return df


@action(name="GetHistoricalTrendAndFanCharacteristics")
@handle_large_data()
def stock_hot_rank_detail_em(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get recent ranking and fan characteristics data for a specified A-share stock.

    Parameters:
    - symbol: Ticker symbol of specific stock with market abbreviation (e.g., "SZ000665" with Shenzhen Stock Exchange).
    
    Return:
        ['时间', '排名', '证券代码', '新晋粉丝', '铁杆粉丝']
    """
    df = ak.stock_hot_rank_detail_em(symbol=symbol)
    
    return df


@action(name="GetHistoricalTrendHK")
@handle_large_data()
def stock_hk_hot_rank_detail_em(symbol: str,
                                ) -> pd.DataFrame:
    """
    Get recent ranking data for a specified stock on Hong Kong stock Exchange.

    Parameters:
    - symbol: Ticker symbol of specific HKEX stock (e.g., "00700").
    
    Return:
        ['时间', '排名', '证券代码']
    """
    df = ak.stock_hk_hot_rank_detail_em(symbol=symbol)
    
    return df


@action(name="GetRecentRankingHistory")
@handle_large_data()
def stock_hot_rank_detail_realtime_em(symbol: str,
                                      ) -> pd.DataFrame:
    """
    Get recent ranking data for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock with market abbreviation, e.g., "SZ000665" with Shenzhen Stock Exchange.
    
    Return:
        ['时间', '排名']
    """
    df = ak.stock_hot_rank_detail_realtime_em(symbol=symbol)
    
    return df


@action(name="GetHotKeywords")
@handle_large_data()
def stock_hot_keyword_em(symbol: str,
                         ) -> pd.DataFrame:
    """
    Get the hotspot data for a specified A-share stock on the most recent trading day.

    Parameters:
    - symbol: The ticker symbol of specific stock with market abbreviation, e.g., "SZ000665" with Shenzhen Stock Exchange.
    
    Return:
        ['时间', '股票代码', '概念名称', '概念代码', '热度']
    """
    df = ak.stock_hot_keyword_em(symbol=symbol)
    
    return df


@action(name="GetHotSearchStocks")
@handle_large_data()
def stock_hot_search_baidu(
    symbol: str = "A股", date: str = datetime_utils.yyyymmdd(), time: str = "今日",
    ) -> pd.DataFrame:
    """
    Get the hot search stock data for A-shares, Hong Kong stocks, and U.S. stocks on a specified date and time.

    Parameters:
    - symbol: The market symbol, e.g., "A股". Choices are {"全部", "A股", "港股", "美股"}.
    - date: The date format 'YYYYMMDD', e.g., "20230421".
    - time: The time period, e.g., "今日". Choices are {"今日", "1小时"}.
    
    Return:
        ['股票名称', '涨跌幅', '所属板块名称', '市场代码', '现价', '市场缩写', '排名变化', '市场']
    """
    df = ak.stock_hot_search_baidu(symbol=symbol, date=date, time=time)
    
    return df


@action(name="GetRelatedStocks")
@handle_large_data()
def stock_hot_rank_relate_em(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get recent related stock data for a specified A-share stock.

    Parameters:
    - symbol: The ticker symbol of specific stock with market abbreviation, e.g., "SZ000665" with Shenzhen Stock Exchange.
    
    Return:
        ['时间','股票代码', '相关股票代码', '涨跌幅']
    """
    df = ak.stock_hot_rank_relate_em(symbol=symbol)
    
    return df

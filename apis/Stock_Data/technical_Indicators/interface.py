import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetStocksHittingNewHighs")
@handle_large_data()
def stock_rank_cxg_ths(symbol: str = "创月新高",
                       ) -> pd.DataFrame:
    """
    Get data on specified A-share stocks reaching new highs within a specified time period.

    Parameters:
    - symbol: The type of new high to retrieve, choice of {"创月新高", "半年新高", "一年新高", "历史新高"}.
    
    Return:
        ['股票代码', '股票简称', '涨跌幅', '换手率', '最新价', '前期高点', '前期高点日期']
    """
    df = ak.stock_rank_cxg_ths(symbol=symbol)
    
    return df


@action(name="GetNewLowStocks")
@handle_large_data()
def stock_rank_cxd_ths(symbol: str = "创月新低",
                       ) -> pd.DataFrame:
    """
    Get data on specified A-share stocks reaching new lows within a specified time period.

    Parameters:
    - symbol: The type of new lows, choices of {"创月新低", "半年新低", "一年新低", "历史新低"}.
    
    Return:
        ['股票代码', '股票简称', '涨跌幅', '换手率', '最新价', '前期低点', '前期低点日期']
    """
    df = ak.stock_rank_cxd_ths(symbol=symbol)
    
    return df


@action(name="GetConsecutiveRises")
@handle_large_data()
def stock_rank_lxsz_ths(
    ) -> pd.DataFrame:
    """
    Get data on A-share stocks with consecutive price increases.
    
    Return:
        ['股票代码', '股票简称', '收盘价', '最高价', '最低价', '连涨天数', '连续涨跌幅', '累计换手率', '所属行业']
    """
    df = ak.stock_rank_lxsz_ths()
    
    return df


@action(name="GetConsecutiveDeclines")
@handle_large_data()
def stock_rank_lxxd_ths() -> pd.DataFrame:
    """
    Get data on A-share stocks with consecutive price declines.
    
    Return:
        ['股票代码', '股票简称', '收盘价', '最高价', '最低价', '连涨天数', '连续涨跌幅', '累计换手率', '所属行业']
    """
    df = ak.stock_rank_lxxd_ths()
    
    return df


@action(name="GetSustainedVolumeIncrease")
@handle_large_data()
def stock_rank_cxfl_ths() -> pd.DataFrame:
    """
    Get data on A-share stocks with sustained volume increases.
    
    Return:
        ['股票代码', '股票简称', '涨跌幅', '最新价', '成交量', '基准日成交量', '放量天数', '阶段涨跌幅', '所属行业']
    """
    df = ak.stock_rank_cxfl_ths()
    
    return df


@action(name="GetSustainedVolumeDecrease")
@handle_large_data()
def stock_rank_cxsl_ths() -> pd.DataFrame:
    """
    Get data on A-share stocks with sustained volume decreases.
    
    Return:
        ['股票代码', '股票简称', '涨跌幅', '最新价', '成交量', '基准日成交量', '缩量天数', '阶段涨跌幅', '所属行业']
    """
    df = ak.stock_rank_cxsl_ths()
    
    return df


@action(name="GetUpwardBreakouts")
@handle_large_data()
def stock_rank_xstp_ths(symbol: str = "5日均线",
                        ) -> pd.DataFrame:
    """
    Get data of A-Shares stocks with upward breakouts.

    Parameters:
    - symbol: The type of moving average, choices of {"5日均线", "10日均线", "20日均线", "30日均线", "60日均线", "90日均线", "250日均线", "500日均线"}.
    
    Return:
        ['股票代码', '股票简称', '最新价', '成交额', '成交量', '涨跌幅', '换手率']
    """
    df = ak.stock_rank_xstp_ths(symbol=symbol)
    
    return df


@action(name="GetDownwardBreakouts")
@handle_large_data()
def stock_rank_xxtp_ths(symbol: str = "5日均线",
                        ) -> pd.DataFrame:
    """
    Get data of A-Shares stocks with downward breakouts.

    Parameters:
    - symbol: The type of moving average, choices of {"5日均线", "10日均线", "20日均线", "30日均线", "60日均线", "90日均线", "250日均线", "500日均线"}.
    
    Return:
        ['股票代码', '股票简称', '最新价', '成交额', '成交量', '涨跌幅', '换手率']
    """
    df = ak.stock_rank_xxtp_ths(symbol=symbol)
    
    return df


@action(name="GetSimultaneousRiseInPriceAndVolume")
@handle_large_data()
def stock_rank_ljqs_ths() -> pd.DataFrame:
    """
    Get data on A-share stocks with both volume and price increasing.
    
    Return:
        ['股票代码', '股票简称', '最新价', '量价齐升天数', '阶段涨幅', '累计换手率', '所属行业']
    """
    df = ak.stock_rank_ljqs_ths()
    
    return df


@action(name="GetSimultaneousDeclineInPriceAndVolume")
@handle_large_data()
def stock_rank_ljqd_ths() -> pd.DataFrame:
    """
    Get data of stocks with simultaneous decline in price and volume.
    
    Return:
        ['股票代码', '股票简称', '最新价', '量价齐跌天数', '阶段涨幅', '累计换手率', '所属行业']
    """
    df = ak.stock_rank_ljqd_ths()
    
    return df


@action(name="GetInsuranceShareholding")
@handle_large_data()
def stock_rank_xzjp_ths() -> pd.DataFrame:
    """
    Get data on A-share stocks with insurance capital holding a significant stake.
    
    Return:
        ['举牌公告日', '股票代码', '股票简称', '现价', '涨跌幅', '举牌方', '增持数量', '交易均价', '增持数量占总股本比例', '变动后持股总数', '变动后持股比例']
    """
    df = ak.stock_rank_xzjp_ths()
    
    return df

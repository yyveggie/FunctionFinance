import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import akshare as ak
import pandas as pd
from crawler import datetime_utils, utils


@action(name="GetBlockTradingMarketStatistics")
@handle_large_data()
def stock_dzjy_sctj() -> pd.DataFrame:
    """
    Get all market statistics for block trading.
    
    Return:
        ['交易日期', '上证指数', '上证指数涨跌幅', '大宗交易成交总额', '溢价成交总额', '溢价成交总额占比', '折价成交总额', '折价成交总额占比']
    """
    return ak.stock_dzjy_sctj()


@action(name="GetBlockTradingDailyDetails")
@handle_large_data()
def stock_dzjy_mrmx(
    symbol: str, start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get the block trade data among institutions during the specified period.

    Parameter:
    - symbol: Type of securities, choice of {'A股', 'B股', '基金', '债券'}.
    - start_date: Start date, e.g., '20220104'.
    - end_date: End date, e.g., '20220104'.
    
    Return:
        ['交易日期', '证券代码', '证券简称', '涨跌幅', '收盘价', '成交价', '折溢率', '成交量', '成交额', '成交额/流通市值', '买方营业部', '卖方营业部']
    """
    return ak.stock_dzjy_mrmx(symbol=symbol, start_date=start_date, end_date=end_date)


@action(name="GetBlockTradingDailyStatistics")
@handle_large_data()
def stock_dzjy_mrtj(start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),) -> pd.DataFrame:
    """
    Get the block trading data of various institutions during the specified time period.

    Parameter:
    - start_date: Start date, e.g., '20220105'.
    - end_date: End date, e.g., '20220105'.
    
    Return:
        ['交易日期', '证券代码', '证券简称', '涨跌幅', '收盘价', '成交均价', '折溢率', '成交笔数', '成交总量', '成交总额', '成交总额/流通市值']
    """
    return ak.stock_dzjy_mrtj(start_date=start_date, end_date=end_date)


@action(name="GetActiveASharesStatistics")
@handle_large_data()
def stock_dzjy_hygtj(symbol: str = "近六月",
                     ) -> pd.DataFrame:
    """
    Get statistics for active A-shares stocks during the specified time period.

    Parameter:
    - symbol: Time period symbol, choice of {'近一月', '近三月', '近六月', '近一年'}.
    
    Return:
        ['证券代码', '证券简称', '最新价', '涨跌幅', '最近上榜日', '上榜次数-总计', '上榜次数-溢价', '上榜次数-折价', '总成交额', '折溢率', '成交总额/流通市值', '上榜日后平均涨跌幅-1日', '上榜日后平均涨跌幅-5日', '上榜日后平均涨跌幅-10日', '上榜日后平均涨跌幅-20日']
    """
    return ak.stock_dzjy_hygtj(symbol=symbol)

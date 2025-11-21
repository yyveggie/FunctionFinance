import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="RetrieveGoodwillImpairmentExpectations")
@handle_large_data()
def stock_sy_yq_em(date: str = datetime_utils.year() + "-12-31") -> pd.DataFrame:
    """
    Get all goodwill impairment detail data for A-shares stock.

    Parameters:
    - date (str): You can only select the end of the year date, which is XXXX-12-31, for example, 2022-12-31.
    
    Return:
        ['股票代码', '股票简称', '业绩变动原因', '最新商誉报告期', '最新一期商誉', '上年商誉', '预计净利润-下限', '预计净利润-上限', '业绩变动幅度-下限', '业绩变动幅度-上限', '上年度同期净利润', '公告日期', '交易市场']
    """
    return ak.stock_sy_yq_em(date=date)


@action(name="RetrieveIndividualGoodwill")
@handle_large_data()
def stock_sy_em(date: str = datetime_utils.year() + "-12-31") -> pd.DataFrame:
    """
    Get all individual stock goodwill detail data for A-shares stock.

    Parameters:
    - date (str): You can only select the end of the year date, which is XXXX-12-31, for example, 2022-12-31.
    
    Return:
        ['股票代码', '股票简称', '商誉', '商誉占净资产比例', '净利润', '净利润同比', '上年商誉', '公告日期', '交易市场']
    """
    return ak.stock_sy_em(date=date)


@action(name="RetrieveIndividualGoodwillImpairment")
@handle_large_data()
def stock_sy_jz_em(date: str = datetime_utils.year() + "-12-31") -> pd.DataFrame:
    """
    Get detailed data on goodwill impairment for all individual A-share stocks.

    Parameters:
    - date (str): You can only select the end of the year date, which is XXXX-12-31, for example, 2022-12-31.
    
    Return:
        ['股票代码', '股票简称', '商誉', '商誉减值', '商誉减值占净资产比例', '净利润', '商誉减值占净利润比例', '公告日期', '交易市场']
    """
    return ak.stock_sy_jz_em(date=date)


@action(name="RetrieveIndustryGoodwill")
@handle_large_data()
def stock_sy_hy_em(date: str = datetime_utils.year() + "-12-31") -> pd.DataFrame:
    """
    Get goodwill information data for different industries.

    Parameters:
    - date (str): You can only select the end of the year date, which is XXXX-12-31, for example, 2022-12-31.
    
    Return:
        ['行业名称', '公司家数', '商誉规模', '净资产', '商誉规模占净资产规模比例', '净利润规模']
    """
    return ak.stock_sy_hy_em(date=date)


@action(name="RetrieveGoodwillMarketOverview")
@handle_large_data()
def stock_sy_profile_em() -> pd.DataFrame:
    """
    Get historical market overview data on goodwill in the A-share market.
    
    Return:
        ['报告期', '商誉', '商誉减值', '净资产', '商誉占净资产比例', '商誉减值占净资产比例', '净利润规模', '商誉减值占净利润比例']
    """
    return ak.stock_sy_profile_em()

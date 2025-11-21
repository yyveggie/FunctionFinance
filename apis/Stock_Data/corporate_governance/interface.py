import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from typing import List, Optional, Any
from actionweaver import action
import akshare as ak
import pandas as pd
from crawler import datetime_utils, utils


@action(name="GetPledgeRatioDetail")
@handle_large_data()
def stock_gpzy_pledge_ratio_detail_em() -> pd.DataFrame:
    """
    Get all historical detailed information on the pledge of shares by important shareholders in the stock pledge market.
    
    Return:
        ['股票代码', '股票简称', '股东名称', '质押股份数量', '占所持股份比例', '占总股本比例', '质押机构', '最新价', '质押日收盘价', '预估平仓线', '公告日期', '质押开始日期']
    """
    return ak.stock_gpzy_pledge_ratio_detail_em()


@action(name="GetIndustryDataPledgeRatio")
@handle_large_data()
def stock_gpzy_industry_data_em() -> pd.DataFrame:
    """
    Get all historical data on the pledge ratio of listed companies.
    """
    return ak.stock_gpzy_industry_data_em()


@action(name="GetStockPledgeMarketOverview")
@handle_large_data()
def stock_gpzy_profile_em() -> pd.DataFrame:
    """
    Get the overview of the stock pledge market.
    """
    return ak.stock_gpzy_profile_em()


@action(name="GetSecuritiesPledgeInstitutionDistributionStatistics")
@handle_large_data()
def stock_gpzy_distribute_statistics_company_em() -> pd.DataFrame:
    """
    Get historical data on the distribution statistics of pledge institutions for securities companies.
    """
    return ak.stock_gpzy_distribute_statistics_company_em()


@action(name="GetBankPledgeInstitutionDistributionStatistics")
@handle_large_data()
def stock_gpzy_distribute_statistics_bank_em() -> pd.DataFrame:
    """
    Get historical data on the distribution statistics of pledge institutions for banks.
    """
    return ak.stock_gpzy_distribute_statistics_bank_em()


@action(name="GetPledgeRatio")
@handle_large_data()
def stock_gpzy_pledge_ratio_em(date: str=datetime_utils.yyyymmdd()) -> pd.DataFrame:
    """
    Get the pledge ratio of all listed companies on the specified date.
    
    Parameters:
    - date: The date for which the pledge ratio of all listed companies are requested in the format "YYYYMMDD".
    """
    return ak.stock_gpzy_pledge_ratio_em(date=date)


@action(name="GetExternalGuarantees")
@handle_large_data()
def stock_cg_guarantee_cninfo(
    symbol: str, 
    start_date: str = "19000101", 
    end_date: str = datetime_utils.yyyymmdd()
    ) -> pd.DataFrame:
    """
    Get data on external guarantees.

    Parameters:
    - symbol: The type of stock, choice of {"全部", "深市主板", "沪市", "创业板", "科创板"}.
    - start_date: The start date in the format "YYYYMMDD".
    - end_date: The end date in the format "YYYYMMDD".
    """
    return ak.stock_cg_guarantee_cninfo(
        symbol=symbol, start_date=start_date, end_date=end_date
    )


@action(name="GetCompanyLawsuits")
@handle_large_data()
def stock_cg_lawsuit_cninfo(
    symbol: str, start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd()) -> pd.DataFrame:
    """
    Get data on company lawsuits.

    Parameters:
    - symbol: The type of stock, choice of {"全部", "深市主板", "沪市", "创业板", "科创板"}.
    - start_date: The start date in the format "YYYYMMDD".
    - end_date: The end date in the format "YYYYMMDD".
    """
    return ak.stock_cg_lawsuit_cninfo(
        symbol=symbol, start_date=start_date, end_date=end_date
    )


@action(name="GetEquityMortgage")
@handle_large_data()
def stock_cg_equity_mortgage_cninfo(date: str = datetime_utils.yyyymmdd()) -> pd.DataFrame:
    """
    Get data on equity mortgage of specific date.

    Parameters:
    - date (str): The date in the format "YYYYMMDD".
    """
    return ak.stock_cg_equity_mortgage_cninfo(
        date=date)

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetSettlementExchangeRate_SZHK")
@handle_large_data()
def stock_sgt_settlement_exchange_rate_szse() -> pd.DataFrame:
    """
    Get settlement exchange rate information for Shenzhen-Hong Kong Stock Connect.
    
    Return:
        ['适用日期', '买入结算汇兑比率', '卖出结算汇兑比率', '货币种类']
    """
    df = ak.stock_sgt_settlement_exchange_rate_szse()
    
    return df


@action(name="GetSettlementExchangeRate_SHHK")
@handle_large_data()
def stock_sgt_settlement_exchange_rate_sse() -> pd.DataFrame:
    """
    Get settlement exchange rate information for Shanghai-Hong Kong Stock Connect.
    
    Return:
        ['适用日期', '买入结算汇兑比率', '卖出结算汇兑比率', '货币种类']
    """
    df = ak.stock_sgt_settlement_exchange_rate_sse()
    
    return df


@action(name="GetReferenceExchangeRate_SZHK")
@handle_large_data()
def stock_sgt_reference_exchange_rate_szse() -> pd.DataFrame:
    """
    Get all Shenzhen-Hong Kong Stock Connect reference exchange rate data.
    
    Return:
        ['适用日期', '参考汇率买入价', '参考汇率卖出价', '货币种类']
    """
    df = ak.stock_sgt_reference_exchange_rate_szse()
    
    return df


@action(name="GetReferenceExchangeRate_SHHK")
@handle_large_data()
def stock_sgt_reference_exchange_rate_sse() -> pd.DataFrame:
    """
    Get all Shanghai-Hong Kong Stock Connect reference exchange rate data.
    
    Return:
        ['适用日期', '参考汇率买入价', '参考汇率卖出价', '货币种类']
    """
    df = ak.stock_sgt_reference_exchange_rate_sse()
    
    return df


@action(name="GetHKGGTComponents")
@handle_large_data()
def stock_hk_ggt_components_em() -> pd.DataFrame:
    """
    Get all Hong Kong Stock Connect constituent stock quote data.
    
    Return:
        ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '今开', '最高', '最低', '昨收', '成交量', '成交额']
    """
    df = ak.stock_hk_ggt_components_em()
    
    return df


@action(name="GetIntradayFundFlow")
@handle_large_data()
def stock_hsgt_fund_min_em(symbol: str,
                           ) -> pd.DataFrame:
    """
    Get Shanghai-Shenzhen-Hong Kong Stock Connect intraday data.

    Parameters:
    - symbol: The choice of {"北向资金", "南向资金"}.
    
    Return:
        ['日期', '时间', '沪股通', '深股通', '北向资金']
    """
    df = ak.stock_hsgt_fund_min_em(symbol=symbol)
    
    return df


@action(name="GetIndividualStockRanking")
@handle_large_data()
def stock_hsgt_hold_stock_em(market: str, indicator: str = "今日排行",
                             ) -> pd.DataFrame:
    """
    Get the individual stock rankings of Shanghai-Shenzhen-Hong Kong Stock Connect holdings within a specified time period.

    Parameters:
    - market: The choice of {"北向", "沪股通", "深股通"}.
    - indicator: The choice of {"今日排行", "3日排行", "5日排行", "10日排行", "月排行", "季排行", "年排行"}.
    
    Return:
        ['代码', '名称', '今日收盘价', '今日涨跌幅', '今日持股-股数', '今日持股-市值', '今日持股-占流通股比', '今日持股-占总股本比', '增持估计-股数', '增持估计-市值', '增持估计-市值增幅', '增持估计-占流通股比', '增持估计-占总股本比', '所属板块', '日期']
    """
    df = ak.stock_hsgt_hold_stock_em(market=market, indicator=indicator)
    
    return df


@action(name="GetDailyStockStatistics")
@handle_large_data()
def stock_hsgt_stock_statistics_em(
    symbol: str, start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get all Shanghai-Shenzhen-Hong Kong Stock Connect holdings data within a specified time period.

    Parameters:
    - symbol: The choice of {"北向持股", "沪股通持股", "深股通持股", "南向持股"}.
    - start_date: The start date in the format "YYYYMMDD".
    - end_date: The end date in the format "YYYYMMDD".
    
    Return:
        ['持股日期', '股票代码', '股票简称', '当日收盘价', '当日涨跌幅', '持股数量', '持股市值', '持股数量占发行股百分比', '持股市值变化-1日', '持股市值变化-5日', '持股市值变化-10日']
    """
    df = ak.stock_hsgt_stock_statistics_em(
        symbol=symbol, start_date=start_date, end_date=end_date
    )
    
    return df


@action(name="GetInstitutionRanking")
@handle_large_data()
def stock_hsgt_institution_statistics_em(
        market: str, 
        start_date: str = "19000101", 
        end_date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get data on changes in the number of shares held by different institutions in the Shanghai-Shenzhen-Hong Kong Stock Connect within a specified time period.

    Parameters:
    - market: Choice of {"北向持股", "沪股通持股", "深股通持股", "南向持股"}.
    - start_date: Start date in the format "YYYYMMDD".
    - end_date: End date in the format "YYYYMMDD".
    
    Return:
        ['持股日期', '机构名称', '持股只数', '持股市值', '持股市值变化-1日', '持股市值变化-5日', '持股市值变化-10日']
    """
    return ak.stock_hsgt_institution_statistics_em(
        market=market, start_date=start_date, end_date=end_date
    )


@action(name="GetHSGTHistoricalData")
@handle_large_data()
def stock_hsgt_hist_em(symbol: str,
                       ) -> pd.DataFrame:
    """
    Get all historical quote data for Shanghai-Shenzhen-Hong Kong Stock Connect.

    Parameters:
    - symbol: Choice of {"沪股通", "深股通", "港股通沪", "港股通深"}.
    
    Return:
        ['日期', '当日成交净买额', '买入成交额', '卖出成交额', '历史累计净买额', '当日资金流入', '当日余额', '领涨股', '领涨股涨跌幅', '上证指数', '涨跌幅']
    """
    df = ak.stock_hsgt_hist_em(symbol=symbol)
    
    return df


@action(name="GetHSGTIndividualStocks")
@handle_large_data()
def stock_hsgt_individual_em(stock: str,
                             ) -> pd.DataFrame:
    """
    Get recent data on the change in market value of holdings for a specified stock in Shanghai-Shenzhen-Hong Kong Stock Connect.

    Parameters:
    - stock: The ticker symbol of specific stock, e.g., "002008".
    
    Return:
        ['持股日期', '当日收盘价', '当日涨跌幅', '持股数量', '持股市值', '持股数量占A股百分比', '持股市值变化-1日', '持股市值变化-5日', '持股市值变化-10日']
    """
    df = ak.stock_hsgt_individual_em(stock=stock)
    
    return df
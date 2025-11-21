import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import akshare as ak
import pandas as pd
from crawler import datetime_utils


@action(name="GetShareholderMeetingData")
@handle_large_data()
def stock_gddh_em() -> pd.DataFrame:
    """
    Get all information data about shareholder meetings.
    
    Return:
        ['代码', '简称', '股东大会名称', '召开开始日', '股权登记日', '现场登记日', '网络投票时间-开始日', '网络投票时间-结束日', '决议公告日', '公告日', '序列号', '提案']
    """
    df = ak.stock_gddh_em()
    
    return df


@action(name="GetSignificantContractData")
@handle_large_data()
def stock_zdhtmx_em(
    start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get details of all significant contracts for A-shares within a specified time period.

    Parameters Type 1:
    - start_date: Start date of the time period to be queried in format 'YYYYMMDD'.
    - end_date: End date of the time period to be queried in format 'YYYYMMDD'.
    
    Return:
        ['股票代码', '股票简称', '签署主体', '签署主体-与上市公司关系', '其他签署方', '其他签署方-与上市公司关系', '合同类型', '合同名称', '合同金额', '上年度营业收入', '占上年度营业收入比例', '最新财务报表的营业收入', '签署日期', '公告日期']
    """
    df = ak.stock_zdhtmx_em(start_date=start_date, end_date=end_date)
    
    return df


@action(name="GetStockResearchReports")
@handle_large_data()
def stock_research_report_em(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get information of research reports for A-shares specific stock.

    Parameters:
    - symbol: Ticker symbol of specific stock you want to query.
    
    Return:
        ['股票代码', '股票简称', '报告名称', '东财评级', '机构', '近一月个股研报数', '2023-盈利预测-收益', '2023-盈利预测-市盈率', '2024-盈利预测-收益', '2024-盈利预测-市盈率', '行业', '日期']
    """
    df = ak.stock_research_report_em(symbol=symbol)
    
    return df


@action(name="GetStockAnnouncements")
@handle_large_data()
def stock_notice_report(symbol: str, date: str = datetime_utils.yyyymmdd(),
                        ) -> pd.DataFrame:
    """
    Get announcements data for A-shares in specific date.

    Parameters:
    - symbol: Ticker symbol of specific stock you want to query.
    - date: You want to query the release date of the announcement in format 'YYYYMMDD'.
    
    Return:
        ['代码', '名称', '公告标题', '公告类型', '公告日期']
    """
    df = ak.stock_notice_report(symbol=symbol, date=date)
    
    return df


@action(name="GetFinancialStatements")
@handle_large_data()
def stock_financial_report_sina(stock: str, symbol: str,
                                ) -> pd.DataFrame:
    """
    Get all historical data of the three major financial statements (balance sheet, income statement, cash flow statement) for a specified A-share stock.

    Parameters:
    - stock: Stock ticker with market identifier, e.g., "sh600600" with Shanghai Stock Exchange.
    - symbol: Choice of {"资产负债表", "利润表", "现金流量表"}.
    
    Return:
        Each statement contains hundreds of extremely detailed features.
    """
    df = ak.stock_financial_report_sina(stock=stock, symbol=symbol)
    return df


@action(name="GetBalanceSheetByReport")
@handle_large_data()
def stock_balance_sheet_by_report_em(symbol: str,
                                     ) -> pd.DataFrame:
    """
    Get all balance sheet historical data for a specific A-Shares stock, sorted by report period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contain hundreds of extremely detailed features.
    """
    df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
    
    return df


@action(name="GetBalanceSheetByYearly")
@handle_large_data()
def stock_balance_sheet_by_yearly_em(symbol: str,
                                     ) -> pd.DataFrame:
    """
    Get all balance sheet historical data for a specific A-Shares stock, sorted by yearly period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contain hundreds of extremely detailed features.
    """
    df = ak.stock_balance_sheet_by_yearly_em(symbol=symbol)
    
    return df


@action(name="GetProfitSheetByReport")
@handle_large_data()
def stock_profit_sheet_by_report_em(symbol: str,
                                    ) -> pd.DataFrame:
    """
    Get all income statement historical data for a specific A-Shares stock, sorted by report period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contain hundreds of extremely detailed features.
    """
    df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
    
    return df


@action(name="GetProfitSheetByYearly")
@handle_large_data()
def stock_profit_sheet_by_yearly_em(symbol: str,
                                    ) -> pd.DataFrame:
    """
    Get all income statement historical data for a specific A-Shares stock, sorted by yearly period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contain hundreds of extremely detailed features.
    """
    df = ak.stock_profit_sheet_by_yearly_em(symbol=symbol)
    
    return df


@action(name="GetProfitSheetByQuarterly")
@handle_large_data()
def stock_profit_sheet_by_quarterly_em(symbol: str,
                                       ) -> pd.DataFrame:
    """
    Get all income statement historical data for a specific A-Shares stock, sorted by quarterly.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contain hundreds of extremely detailed features.
    """
    df = ak.stock_profit_sheet_by_quarterly_em(symbol=symbol)
    
    return df


@action(name="GetCashFlowSheetByReport")
@handle_large_data()
def stock_cash_flow_sheet_by_report_em(symbol: str,
                                       ) -> pd.DataFrame:
    """
    Get all cash flow statements historical data for a specific A-Shares stock, sorted by report period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contains hundreds of extremely detailed features.
    """
    df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
    
    return df


@action(name="GetCashFlowSheetByYearly")
@handle_large_data()
def stock_cash_flow_sheet_by_yearly_em(symbol: str,
                                       ) -> pd.DataFrame:
    """
    Get all cash flow statements historical data for a specific A-Shares stock, sorted by yearly period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contains hundreds of extremely detailed features.
    """
    df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=symbol)
    
    return df


@action(name="GetCashFlowSheetByQuarterly")
@handle_large_data()
def stock_cash_flow_sheet_by_quarterly_em(symbol: str,
                                          ) -> pd.DataFrame:
    """
    Get all cash flow statements historical data for a specific A-Shares stock, sorted by quarterly period.

    Parameters:
    - symbol: Stock ticker with market identifier, e.g., "SH600519" with Shanghai Stock Exchange.
    
    Return:
        Contains hundreds of extremely detailed features.
    """
    df = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=symbol)
    
    return df


@action(name="GetBalanceSheet")
@handle_large_data()
def stock_financial_debt_ths(symbol: str, indicator: str = "按报告期",
                             ) -> pd.DataFrame:
    """
    Get all historical balance sheet data for a specified A-share stock, with options to sort by reporting period, annual, or quarterly.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "000063".
    - indicator: Sorting indicator, choice of {"按报告期", "按年度", "按单季度"}.
    
    Return:
        Contains dozens of extremely detailed features.
    """
    df = ak.stock_financial_debt_ths(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetProfitStatement")
@handle_large_data()
def stock_financial_benefit_ths(symbol: str, indicator: str = "按报告期",
                                ) -> pd.DataFrame:
    """
    Get all historical income statement data for a specified A-share stock, with options to sort by reporting period, annual, or quarterly.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "000063".
    - indicator: Sorting indicator, choice of {"按报告期", "按年度", "按单季度"}.
    
    Return:
        Contains dozens of extremely detailed features.
    """
    df = ak.stock_financial_benefit_ths(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetFlowStatement")
@handle_large_data()
def stock_financial_cash_ths(symbol: str, indicator: str = "按报告期",
                             ) -> pd.DataFrame:
    """
    Get all historical cash flow statement data for a specified A-share stock, with options to sort by reporting period, annual, or quarterly.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "000063".
    - indicator: Sorting indicator, choice of {"按报告期", "按年度", "按单季度"}.
    
    Return:
        Contains dozens of extremely detailed features.
    """
    df = ak.stock_financial_cash_ths(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetFinancialHKReportEM")
@handle_large_data()
def stock_financial_hk_report_em(stock: str, symbol: str, indicator: str = "报告期",
                                 ) -> pd.DataFrame:
    """
    Get all historical data of the three major financial statements (balance sheet, income statement, cash flow statement) for a specified Hong Kong Stock Exchange stock.

    Parameters:
    - stock: Ticker symbol of specific HKEX stock, e.g., "00700".
    - symbol: Type of financial statement, choice of {"资产负债表", "利润表", "现金流量表"}.
    - indicator: Sorting indicator, choice of {"年度", "报告期"}.
    
    Return:
        ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 'REPORT_DATE', 'DATE_TYPE_CODE', 'FISCAL_YEAR', 'STD_ITEM_CODE', 'STD_ITEM_NAME', 'AMOUNT', 'STD_REPORT_DATE']
    """
    df = ak.stock_financial_hk_report_em(
        stock=stock, symbol=symbol, indicator=indicator
    )
    
    return df


@action(name="GetKeyFinancialIndicators")
@handle_large_data()
def stock_financial_abstract(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get key financial indicators, including various financial ratios and performance metrics for a specific A-share stock.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "600004".
    
    Return:
        ['选项', '各类指标', '报告期1', '报告期2', '报告期3'...]
    """
    df = ak.stock_financial_abstract(symbol=symbol)
    
    return df


@action(name="GetKeyFinancialIndicators2")
@handle_large_data()
def stock_financial_abstract_ths(symbol: str, indicator: str = "按报告期",
                                 ) -> pd.DataFrame:
    """
    Get historical data of all major financial indicators for a specified A-share stock.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "600004".
    - indicator: Choice of time period for data retrieval, choice of {"按报告期", "按年度", "按单季度"}.
    
    Return:
        ['报告期', '净利润', '净利润同比增长率', '扣非净利润', '扣非净利润同比增长率', '营业总收入', '营业总收入同比增长率', '基本每股收益', '每股净资产', '每股资本公积金', '每股未分配利润', '每股经营现金流', '销售净利率', '销售毛利率', '净资产收益率', '净资产收益率-摊薄', '营业周期', '存货周转率', '存货周转天数', '应收账款周转天数', '流动比率', '速动比率', '保守速动比率', '产权比率', '资产负债率']
    """
    df = ak.stock_financial_abstract_ths(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetFinancialAnalysisIndicator")
@handle_large_data()
def stock_financial_analysis_indicator(
    symbol: str, start_year: str = datetime_utils.year(),
    ) -> pd.DataFrame:
    """
    Get historical data of all financial indicators for a specified A-share stock within a specified date range.

    Parameters:
    - symbol: Ticker symbol of specific stock, e.g., "600004".
    - start_year: The starting year for data retrieval, e.g., "2020".
    
    Return:
        Contains dozens of extremely detailed features.
    """
    df = ak.stock_financial_analysis_indicator(
        symbol=symbol, start_year=start_year)
    
    return df


@action(name="GetHKFinancialAnalysisIndicator")
@handle_large_data()
def stock_financial_hk_analysis_indicator_em(symbol: str, indicator: str = "报告期",
                                             ) -> pd.DataFrame:
    """
    Get historical data of all financial indicators for a specified Hong Kong Stock Exchange stock within a specified date range.

    Parameters:
    - symbol: Ticker symbol of specific HKEX stock, e.g., "00700".
    - indicator: The type of data to retrieve, e.g., "年度" for yearly data or "报告期" for report period data.
    
    Return:
        ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 'REPORT_DATE', 'DATE_TYPE_CODE', 'PER_NETCASH_OPERATE', 'PER_OI', 'BPS', 'BASIC_EPS', 'DILUTED_EPS', 'OPERATE_INCOME', 'OPERATE_INCOME_YOY', 'GROSS_PROFIT', 'GROSS_PROFIT_YOY', 'HOLDER_PROFIT', 'HOLDER_PROFIT_YOY', 'GROSS_PROFIT_RATIO', 'EPS_TTM', 'OPERATE_INCOME_QOQ', 'NET_PROFIT_RATIO', 'ROE_AVG', 'GROSS_PROFIT_QOQ', 'ROA', 'HOLDER_PROFIT_QOQ', 'ROE_YEARLY', 'ROIC_YEARLY', 'TAX_EBT', 'OCF_SALES', 'DEBT_ASSET_RATIO', 'CURRENT_RATIO', 'CURRENTDEBT_DEBT', 'START_DATE', 'FISCAL_YEAR', 'CURRENCY', 'IS_CNY_CODE']
    """
    df = ak.stock_financial_hk_analysis_indicator_em(
        symbol=symbol, indicator=indicator
    )
    
    return df


@action(name="RetrieveIndustryPERatio")
@handle_large_data()
def stock_industry_pe_ratio_cninfo(
    symbol: str = "证监会行业分类", date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get the industry price-to-earnings (P/E) ratio data for a specified trading day under a specified institutional industry classification.

    Parameters:
    - symbol (str): The classification system for industries, either "证监会行业分类" or "国证行业分类".
    - date (str): The trading date for which to retrieve the data. e.g. '20210910'
    
    Return:
        ['变动日期', '行业分类', '行业层级', '行业编码', '行业名称', '公司数量', '纳入计算公司数量', '总市值-静态', '净利润-静态', '静态市盈率-加权平均', '静态市盈率-中位数', '静态市盈率-算术平均']
    """
    df = ak.stock_industry_pe_ratio_cninfo(
        symbol=symbol, date=date
    )
    
    return df


@action(name="RetrieveAStockIndicators")
@handle_large_data()
def stock_a_indicator_lg(symbol: str,
                         ) -> pd.DataFrame:
    """
    Get historical individual stock indicators for a specified A-share stock: price-to-earnings ratio, price-to-book ratio, dividend yield.

    Parameters:
    - symbol: Ticker stock symbol, e.g., '000001'. Use 'all' to retrieve data for all stocks.
    
    Return:
        ['trade_date', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_mv']
    """
    df = ak.stock_a_indicator_lg(symbol=symbol)
    
    return df


@action(name="RetrieveAStockDividendYield")
@handle_large_data()
def stock_a_gxl_lg(symbol: str = "上证A股",
                   ) -> pd.DataFrame:
    """
    Get all historical dividend yield data for a specified market.

    Parameters:
    - symbol: The symbol of the stock market,  choice of {"上证A股", "深证A股", "创业板", "科创板"}.
    
    Return:
        ['日期', '股息率']
    """
    df = ak.stock_a_gxl_lg(symbol=symbol)
    
    return df


@action(name="RetrieveMarketCongestionData")
@handle_large_data()
def stock_a_congestion_lg() -> pd.DataFrame:
    """
    Get historical data on market congestion for A-share stocks.
    
    Return:
        ['date', 'close', 'congestion']
    """
    df = ak.stock_a_congestion_lg()
    
    return df


@action(name="RetrieveEquityBondSpreadData")
@handle_large_data()
def stock_ebs_lg() -> pd.DataFrame:
    """
    Get all historical stock-bond yield spread data for A-shares.
    
    Return:
        ['日期', '沪深300指数', '股债利差', '股债利差均线']
    """
    df = ak.stock_ebs_lg()
    
    return df


@action(name="RetrieveBuffettIndicatorData")
@handle_large_data()
def stock_buffett_index_lg() -> pd.DataFrame:
    """
    Get historical data on the Buffett Indicator.
    
    Return:
        ['日期', '收盘价', '总市值', 'GDP','近十年分位数','总历史分位数']
    """
    df = ak.stock_buffett_index_lg()
    
    return df


@action(name="RetrieveAStockTTMLYR")
@handle_large_data()
def stock_a_ttm_lyr() -> pd.DataFrame:
    """
    Get all equal-weighted price-to-earnings ratio and median price-to-earnings ratio data for A-shares.
    
    Return:
        ['date', 'middlePETTM', 'averagePETTM', 'middlePELYR', 'averagePELYR', 'quantileInAllHistoryMiddlePeTtm', 'quantileInRecent10YearsMiddlePeTtm', 'quantileInAllHistoryAveragePeTtm', 'quantileInRecent10YearsAveragePeTtm', 'quantileInAllHistoryMiddlePeLyr', 'quantileInRecent10YearsMiddlePeLyr', 'quantileInAllHistoryAveragePeLyr', 'quantileInRecent10YearsAveragePeLyr', 'close']
    """
    df = ak.stock_a_ttm_lyr()
    
    return df


@action(name="RetrieveAStockAllPB")
@handle_large_data()
def stock_a_all_pb() -> pd.DataFrame:
    """
    Get all equal-weighted and median price-to-book ratio data for A-shares.
    
    Return:
        ['date', 'middlePB', 'equalWeightAveragePB', 'close', 'quantileInAllHistoryMiddlePB', 'quantileInRecent10YearsMiddlePB', 'quantileInAllHistoryEqualWeightAveragePB', 'quantileInRecent10YearsEqualWeightAveragePB']
    """
    df = ak.stock_a_all_pb()
    
    return df


@action(name="RetrieveMainBoardPERatio")
@handle_large_data()
def stock_market_pe_lg(symbol: str = "上证",
                       ) -> pd.DataFrame:
    """
    Get all historical indices and average price-to-earnings ratio data for a specified market.

    Parameters:
    - symbol: The symbol of the stock market, choice of {"上证", "深证", "创业板", "科创版"}.
    
    Return:
        ['日期', '指数', '平均市盈率']
    """
    df = ak.stock_market_pe_lg(symbol=symbol)
    
    return df


@action(name="RetrieveIndexPERatio")
@handle_large_data()
def stock_index_pe_lg(symbol: str = "上证50",
                      ) -> pd.DataFrame:
    """
    Get historical price-to-earnings ratio data for a specified index in A-shares.

    Parameters:
    - symbol: The symbol of the stock index, choice of {"上证50", "沪深300", "上证380", "创业板50", "中证500", "上证180", "深证红利", "深证100", "中证1000", "上证红利", "中证100", "中证800"}.

    Return:
        ['日期', '指数', '等权静态市盈率', '静态市盈率', '静态市盈率中位数', '等权滚动市盈率', '滚动市盈率', '滚动市盈率中位数']
    """
    df = ak.stock_index_pe_lg(symbol=symbol)
    
    return df


@action(name="RetrieveMainBoardPBRatio")
@handle_large_data()
def stock_market_pb_lg(symbol: str = "上证",
                       ) -> pd.DataFrame:
    """
    Get all historical price-to-book ratio data for a specified market.

    Parameters:
    - symbol: The symbol of the stock market, choice of {"上证", "深证", "创业板", "科创版"}.
    
    Return:
        ['日期', '指数', '市净率', '等权市净率', '市净率中位数']
    """
    df = ak.stock_market_pb_lg(symbol=symbol)
    
    return df


@action(name="RetrieveIndexPBRatio")
@handle_large_data()
def stock_index_pb_lg(symbol: str = "上证50",
                      ) -> pd.DataFrame:
    """
    Get historical price-to-book ratio data for a specified index in A-shares.

    Parameters:
    - symbol: The symbol of the stock index, choice of {"上证50", "沪深300", "上证380", "创业板50", "中证500", "上证180", "深证红利", "深证100", "中证1000", "上证红利", "中证100", "中证800"}.

    Return:
        ['日期', '指数', '市净率', '等权市净率', '市净率中位数']
    """
    df = ak.stock_index_pb_lg(symbol=symbol)
    
    return df


@action(name="RetrieveAStockValuation")
@handle_large_data()
def stock_zh_valuation_baidu(
    symbol: str, indicator: str = "总市值", period: str = "近一年",
    ) -> pd.DataFrame:
    """
    Get valuation data for a specified A-share within a specified time range.

    Parameters:
    - symbol: The ticker symbol of the A-share stock. e.g. '002044'
    - indicator: The indicator to retrieve, choice of {"总市值", "市盈率(TTM)", "市盈率(静)", "市净率", "市现率"}.
    - period: The period for which to retrieve data, choice of {"近一年", "近三年", "近五年", "近十年", "全部"}.
    
    Returns features list:
        ['date', 'value']
    """
    df = ak.stock_zh_valuation_baidu(
        symbol=symbol, indicator=indicator, period=period
    )
    
    return df


@action(name="RetrieveHKStockIndicators")
@handle_large_data()
def stock_hk_indicator_eniu(symbol: str, indicator: str = "港股",
                            ) -> pd.DataFrame:
    """
    Get all historical financial Ratios data for a specified Hong Kong Stock Exchange stock.

    Parameters:
    - symbol: The symbol of the Hong Kong Stock Exchange stock.
    - indicator: The indicator to retrieve, choice of {"港股", "市盈率", "市净率", "股息率", "ROE", "市值"}.
    
    Return:
        Varies according to indicator.
    """
    df = ak.stock_hk_indicator_eniu(
        symbol=symbol, indicator=indicator
    )
    
    return df


@action(name="RetrieveHKStockValuation")
@handle_large_data()
def stock_hk_valuation_baidu(
    symbol: str, indicator: str = "总市值", period: str = "近一年",
    ) -> pd.DataFrame:
    """
    Get valuation data for a specified Hong Kong Stock Exchange within a specified time range.

    Parameters:
    - symbol: The ticker symbol of the Hong Kong stock. e.g. '02358'
    - indicator: The indicator to retrieve, choice of {"总市值", "市盈率(TTM)", "市盈率(静)", "市净率", "市现率"}.
    - period: The period for which to retrieve data, choice of {"近一年", "近三年", "近五年", "近十年", "全部"}.
    
    Return:
        ['date', 'value']
    """
    df = ak.stock_hk_valuation_baidu(
        symbol=symbol, indicator=indicator, period=period
    )
    
    return df


@action(name="RetrieveHighLowStatistics")
@handle_large_data()
def stock_a_high_low_statistics(symbol: str = "all",
                                ) -> pd.DataFrame:
    """
    Get the number of stocks making new highs and new lows in different markets.

    Parameters:
    - symbol: The symbol of the market, options: {"all": "全部A股", "sz50": "上证50", "hs300": "沪深300", "zz500": "中证500"}.
    
    Return:
        ['date', 'close', 'high20', 'low20', 'high60', 'low60', 'high120', 'low120']
    """
    df = ak.stock_a_high_low_statistics(
        symbol=symbol)
    
    return df


@action(name="RetrieveBelowNAVStatistics")
@handle_large_data()
def stock_a_below_net_asset_statistics(symbol: str = "全部A股",
                                       ) -> pd.DataFrame:
    """
    Get all historical statistics of stocks trading below book value across different indices for A-shares.

    Parameters:
    - symbol: The symbol of the market or index, choice of {"全部A股", "沪深300", "上证50", "中证500"}.
    
    Return:
        ['date', 'below_net_asset', 'total_company', 'below_net_asset_ratio']
    """
    df = ak.stock_a_below_net_asset_statistics(
        symbol=symbol
    )
    
    return df


@action(name="RetrieveFundHoldings")
@handle_large_data()
def stock_report_fund_hold(date: str, symbol: str = "基金持仓",
                           ) -> pd.DataFrame:
    """
    Get detailed holding data for a specified holding type on a specified date.

    Parameters:
    - symbol: The symbol of the data category, choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}.
    - date: The date of the financial report, format: "xxxx-03-31", "xxxx-06-30", "xxxx-09-30", "xxxx-12-31".
    
    Return:
        ['股票代码', '股票简称', '持有基金家数', '持股总数', '持股市值', '持股变化', '持股变动数值', '持股变动比例']
    """
    df = ak.stock_report_fund_hold(
        symbol=symbol, date=date)
    
    return df


@action(name="RetrieveLHBStockStatistics")
@handle_large_data()
def stock_lhb_stock_statistic_em(symbol: str = "近三月",
                                 ) -> pd.DataFrame:
    """
    Get statistics on individual stocks appearing on the Dragon and Tiger List.

    Parameters:
    - symbol: The time range for the statistics, options: {"近一月", "近三月", "近六月", "近一年"}.
    
    Return:
        ['代码', '名称', '最近上榜日', '收盘价', '涨跌幅', '上榜次数', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额', '龙虎榜总成交额', '买方机构次数', '卖方机构次数', '机构买入净额', '机构买入总额', '机构卖出总额', '近1个月涨跌幅', '近3个月涨跌幅', '近6个月涨跌幅', '近1年涨跌幅']
    """
    df = ak.stock_lhb_stock_statistic_em(
        symbol=symbol)
    
    return df


@action(name="GetIndividualStockStatisticsData")
@handle_large_data()
def stock_lhb_ggtj_sina(recent_day: str = "5",
                        ) -> pd.DataFrame:
    """
    Get statistical data of individual stocks listed on the Dragon and Tiger list within a specified date range.

    Parameters:
    - recent_day: Number of recent days to retrieve data for. Choices are "5" for the last 5 days,
                       "10" for the last 10 days, "30" for the last 30 days, or "60" for the last 60 days.
                       
    Return:
        ['股票代码', '股票名称', '上榜次数', '累积购买额', '累积卖出额', '净额', '买入席位数', '卖出席位数']
    """
    df = ak.stock_lhb_ggtj_sina(symbol=recent_day)
    
    return df


@action(name="GetChiNextRegistrationSystemAuditData")
@handle_large_data()
def stock_register_cyb() -> pd.DataFrame:
    """
    Get all historical information data on companies listed on the Growth Enterprise Market (GEM).
    
    Return:
        ['发行人全称', '审核状态', '注册地', '证监会行业', '保荐机构', '律师事务所', '会计师事务所', '更新日期', '受理日期', '拟上市地点']
    """
    df = ak.stock_register_cyb()
    
    return df


@action(name="GetAdditionalShareIssuanceData")
@handle_large_data()
def stock_qbzf_em() -> pd.DataFrame:
    """
    Get data on additional share issuance of new stocks.
    
    Return:
        ['股票代码', '股票简称', '增发代码', '发行方式', '发行总数', '网上发行', '发行价格', '最新价', '发行日期', '增发上市日期', '锁定期']
    """
    df = ak.stock_qbzf_em()
    
    return df


@action(name="GetRightsIssuesData")
@handle_large_data()
def stock_pg_em() -> pd.DataFrame:
    """
    Get rights issue data for new stocks.
    
    Return:
        ['股票代码', '股票简称', '配售代码', '配股数量', '配股比例', '配股价', '最新价', '配股前总股本', '配股后总股本', '股权登记日', '缴款起始日期', '缴款截止日期', '上市日']
    """
    df = ak.stock_pg_em()
    
    return df


@action(name="GetStockRepurchaseData")
@handle_large_data()
def stock_repurchase_em() -> pd.DataFrame:
    """
    Get all historical data on stock repurchase.
    
    Return:
        ['股票代码', '股票简称', '最新价', '计划回购价格区间', '计划回购数量区间-下限', '计划回购数量区间-上限', '占公告前一日总股本比例-下限', '占公告前一日总股本比例-上限', '计划回购金额区间-下限', '计划回购金额区间-上限', '回购起始时间', '实施进度', '已回购股份价格区间-下限', '已回购股份价格区间-上限', '已回购股份数量', '已回购金额', '最新公告日期']
    """
    df = ak.stock_repurchase_em()
    
    return df

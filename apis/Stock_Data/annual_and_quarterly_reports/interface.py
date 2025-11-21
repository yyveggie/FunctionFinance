import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils, utils
import pandas as pd
import akshare as ak
from typing import List, Optional, Any
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetFinancialPerformanceReports")
@handle_large_data()
def stock_yjbb_em(date: str = datetime_utils.year()) -> pd.DataFrame:
    """
    Get the quarterly earnings reports for all stocks for the specified quarter.

    Parameters:
    - date: The date of the financial performance report in the format "YYYYMMDD", e.g., "20220331". It can be one of the following choices: {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}, indicating the end of each quarter from the year 2010 onwards.

    Returns features list:
        ['股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长', '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长', '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率', '所处行业', '最新公告日期']
    """
    return ak.stock_yjbb_em(date=date)


@action(name="GetEarningsForecasts")
@handle_large_data()
def stock_yjyg_em(date: str = datetime_utils.year()) -> pd.DataFrame:
    """
    Get the quarterly earnings forecast reports for all stocks for the specified quarter.

    Parameters:
    - date: The date of the earnings forecast in the format "YYYYMMDD", e.g., "20200331". It can be one of the following choices: {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}, indicating the end of each quarter from the year 2008 onwards.

    Returns features:
        ['股票代码', '股票简称', '预测指标', '业绩变动', '预测数值', '业绩变动幅度', '业绩变动原因', '预告类型', '上年同期值', '公告日期']
    """
    return ak.stock_yjyg_em(date=date)


@action(name="GetDisclosureAnnouncement")
@handle_large_data()
def stock_zh_a_disclosure_report_cninfo(
        symbol: str,
        market: str = "沪深京",
        category: str = "年报",
        start_date: str = "19000101",
        end_date: str = datetime_utils.year()
        ) -> pd.DataFrame:
    """
    Get the disclosure announcement information for the specified stock.

    Parameters:
    - symbol: The ticker of specific stock for which disclosure reports are requested.
    - market: The market for which disclosure reports are requested, choice of {"沪深京", "港股", "三板", "基金", "债券", "监管", "预披露"}.
    - category: The category of disclosure reports requested, choice of {'年报', '半年报', '一季报', '三季报', '业绩预告', '权益分派', '董事会', '监事会', '股东大会', '日常经营', '公司治理', '中介报告', '首发', '增发', '股权激励', '配股', '解禁', '公司债', '可转债', '其他融资', '股权变动', '补充更正', '澄清致歉', '风险提示', '特别处理和退市', '退市整理期'}.
    - start_date: The start date for which disclosure reports are requested in the format "YYYYMMDD".
    - end_date: The end date for which disclosure reports are requested in the format "YYYYMMDD".
    
    Returns features:
        ['代码', '简称', '公告标题', '公告时间', '公告链接']
    """
    return ak.stock_zh_a_disclosure_report_cninfo(
        symbol=symbol,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )


@action(name="GetDisclosureResearchReports")
@handle_large_data()
def stock_zh_a_disclosure_relation_cninfo(
        symbol: str,
        market: str = "沪深京",
        start_date: str = "19000101",
        end_date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the disclosure research reports information for the specified stock.

    Parameters:
    - symbol: The stock code of the company for which disclosure research reports are requested.
    - market: The market for which disclosure research reports are requested, choice of {"沪深京", "港股", "三板", "基金", "债券", "监管", "预披露"}.
    - start_date: The start date for which disclosure research reports are requested in the format "YYYYMMDD".
    - end_date: The end date for which disclosure research reports are requested in the format "YYYYMMDD".
    
    Returns features:
        ['代码', '简称', '公告标题', '公告时间', '公告链接']
    """
    return ak.stock_zh_a_disclosure_relation_cninfo(
        symbol=symbol, market=market, start_date=start_date, end_date=end_date
    )


@action(name="GetIndustryClassificationData")
@handle_large_data()
def stock_industry_category_cninfo(
        symbol: str = "证监会行业分类标准") -> pd.DataFrame:
    """
    Get industry classification list data using various industry classification standards.

    Parameters:
    - symbol: The industry classification standard. Options include: {'证监会行业分类标准', '巨潮行业分类标准', '申银万国行业分类标准', '新财富行业分类标准', '国资委行业分类标准', '巨潮产业细分标准', '天相行业分类标准', '全球行业分类标准'}.

    Returns features:
        ['类目编码', '类目名称', '终止日期', '行业类型', '行业类型编码', '类目名称英文', '父类编码', '分级']
    """
    return ak.stock_industry_category_cninfo(symbol=symbol)


@action(name="GetShareCapitalChangeInfo")
@handle_large_data()
def stock_share_change_cninfo(
        symbol: str, 
        start_date: str = "19000101", 
        end_date: str = datetime_utils.yyyymmdd(),
        ) -> pd.DataFrame:
    """
    Get the stock capital change data for the specified stock within the specified time range.

    Parameters:
    - symbol: The stock symbol, e.g., "002594".
    - start_date: The start date in the format "YYYYMMDD", e.g., "20091227".
    - end_date: The end date in the format "YYYYMMDD", e.g., "20220708".

    Returns features (Main features):
        ['证券简称', '机构名称', '境外法人持股', '证券投资基金持股', '国家持股-受限', '国有法人持股', '配售法人股', '发起人股份', '未流通股份', '其中：境外自然人持股', '外资持股-受限', '内部职工股', '境外上市外资股-H股', '其中：境内法人持股', '自然人持股', '人民币普通股', '国有法人持股-受限', '一般法人持股', '控股股东、实际控制人', '变动原因', '境内法人持股', '战略投资者持股', '国家持股', '流通受限股份', '优先股', '高管股', '总股本', '其中：限售高管股' ...]
    """
    return ak.stock_share_change_cninfo(
        symbol=symbol, start_date=start_date, end_date=end_date
    )


@action(name="GetAllotmentInfo")
@handle_large_data()
def stock_allotment_cninfo(
        symbol: str, 
        start_date: str = "19000101", 
        end_date: str = datetime_utils.yyyymmdd()
        ) -> pd.DataFrame:
    """
    Get the stock capital change data for the specified stock within the specified time range.

    Parameters:
    - symbol: The stock symbol, e.g., "600030".
    - start_date: The start date in the format "YYYYMMDD", e.g., "19900101".
    - end_date: The end date in the format "YYYYMMDD", e.g., "20221008".
    
    Returns features (Main features):
        ['记录标识', '证券简称', '停牌起始日', '上市公告日期', '配股缴款起始日', '可转配股数量', '停牌截止日', '实际配股数量', '配股价格', '配股比例', '配股前总股本', '每股配权转让费(元)', '法人股实配数量', '实际募资净额', '大股东认购方式', '发行方式', '配股失败，退还申购款日期', '除权基准日', '预计发行费用', '配股发行结果公告日', '证券代码', '配股权证交易截止日', '国家股实配数量' ...]
    """
    return ak.stock_allotment_cninfo(
        symbol=symbol, start_date=start_date, end_date=end_date
    )


@action(name="GetBalanceSheet")
@handle_large_data()
def stock_zcfz_em(date: str) -> pd.DataFrame:
    """
    Get the balance sheets of all A-share stocks at the specified date.

    Parameters:
    - date: The date in the format "YYYYMMDD", where MMDD indicates the quarter-end date, e.g., "20200331".
                 Choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; starting from "20081231".
    
    Returns features:
        ['股票代码', '股票简称', '资产-货币资金', '资产-应收账款', '资产-存货', '资产-总资产', '资产-总资产同比', '负债-应付账款', '负债-总负债', '负债-预收账款', '负债-总负债同比', '资产负债率', '股东权益合计', '公告日期']
    """
    return ak.stock_zcfz_em(date=date)


@action(name="GetIncomeStatement")
@handle_large_data()
def stock_lrb_em(date: str) -> pd.DataFrame:
    """
    Get the income statements of all A-share stocks at the specified date.

    Parameters:
    - date: The date in the format "YYYYMMDD", where MMDD indicates the quarter-end date, e.g., "20200331".
                 Choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; starting from "20120331".
    
    Returns features:
        ['股票代码', '股票简称', '净利润', '净利润同比', '营业总收入', '营业总收入同比', '营业总支出-营业支出', '营业总支出-销售费用', '营业总支出-管理费用', '营业总支出-财务费用', '营业总支出-营业总支出', '营业利润', '利润总额', '公告日期']
    """
    return ak.stock_lrb_em(date=date)


@action(name="GetCashFlowStatement")
@handle_large_data()
def stock_xjll_em(date: str) -> pd.DataFrame:
    """
    Get the cash flow statements of all A-share stocks at the specified date.

    Parameters:
    - date: The date in the format "YYYYMMDD", where MMDD indicates the quarter-end date, e.g., "20200331".
                 Choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; starting from "20081231".
                 
    Returns features:
        ['股票代码', '股票简称', '净现金流-净现金流', '净现金流-同比增长', '经营性现金流-现金流量净额', '经营性现金流-净现金流占比', '投资性现金流-现金流量净额', '投资性现金流-净现金流占比', '融资性现金流-现金流量净额', '融资性现金流-净现金流占比', '公告日期']
    """
    return ak.stock_xjll_em(date=date)

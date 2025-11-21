import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetShareholdersChange")
@handle_large_data()
def stock_ggcg_em(symbol: str,
                  ) -> pd.DataFrame:
    """
    Get the information on stock holding changes of senior executives for all A-share stocks.

    Parameters:
    - symbol: Symbol indicating the type of data to retrieve.
                   Choice of {"全部", "股东增持", "股东减持"}; indicating {"all", "shareholders_increase", "shareholders_decrease"}.
    
    Return:
        ['代码', '名称', '最新价', '涨跌幅', '股东名称', '持股变动信息-增减', '持股变动信息-变动数量', '持股变动信息-占总股本比例', '持股变动信息-占流通股比例', '变动后持股情况-持股总数', '变动后持股情况-占总股本比例', '变动后持股情况-持流通股数', '变动后持股情况-占流通股比例', '变动开始日', '变动截止日', '公告日']
    """
    df = ak.stock_ggcg_em(symbol=symbol)
    
    return df


@action(name="GetTop10CirculatingShareholders")
@handle_large_data()
def stock_gdfx_free_top_10_em(symbol: str, date: str, ) -> pd.DataFrame:
    """
    Get information on the top 10 circulating shareholders of the specific stock on the specified date.

    Parameters:
    - symbol: Ticker symbol of specific stock with market identifier (e.g., "sh688686" with Shanghai Stock Exchange)
    - date: Date of the financial report publication quarter's last day (e.g., "20210630")
    
    Return:
        ['名次', '股东名称', '股东性质', '股份类型', '持股数', '占总流通股本持股比例', '增减', '变动比率']
    """
    df = ak.stock_gdfx_free_top_10_em(symbol=symbol, date=date)
    
    return df


@action(name="GetTop10Shareholders")
@handle_large_data()
def stock_gdfx_top_10_em(symbol: str, date: str,
                         ) -> pd.DataFrame:
    """
    Get information on the top 10 shareholders of the specific stock on the specified date.

    Parameters:
    - symbol: Ticker symbol of specific stock with market identifier (e.g., "sh688686" with Shanghai Stock Exchange)
    - date: Date of the financial report publication quarter's last day (e.g., "20210630")
    
    Return:
        ['名次', '股东名称', '股份类型', '持股数', '占总股本持股比例', '增减', '变动比率']
    """
    df = ak.stock_gdfx_top_10_em(symbol=symbol, date=date)
    
    return df


@action(name="GetTop10CirculatingShareholdersChange")
@handle_large_data()
def stock_gdfx_free_holding_change_em(date: str,
                                      ) -> pd.DataFrame:
    """
    "Get the statistics on stock holding changes of the top 10 circulating shareholders for all A-share stocks on the specified date."

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '期末持股只数统计-总持有', '期末持股只数统计-新进', '期末持股只数统计-增加', '期末持股只数统计-不变', '期末持股只数统计-减少', '流通市值统计', '持有个股']
    """
    df = ak.stock_gdfx_free_holding_change_em(date=date)
    
    return df


@action(name="GetTop10ShareholdersChange")
@handle_large_data()
def stock_gdfx_holding_change_em(date: str,
                                 ) -> pd.DataFrame:
    """
    Get the statistics on stock holding changes of the top 10 shareholders for all A-share stocks on the specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '期末持股只数统计-总持有', '期末持股只数统计-新进', '期末持股只数统计-增加', '期末持股只数统计-不变', '期末持股只数统计-减少', '流通市值统计', '持有个股']
    """
    df = ak.stock_gdfx_holding_change_em(date=date)
    
    return df


@action(name="GetCirculatingShareholdersHoldingAnalysis")
@handle_large_data()
def stock_gdfx_free_holding_analyse_em(date: str,
                                       ) -> pd.DataFrame:
    """
    Get the analysis on stock holding of the top 10 circulating shareholders for all A-share stocks on the specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20230930")
    
    Return:
        ['股东名称', '股东类型', '股票代码', '股票简称', '报告期', '期末持股-数量', '期末持股-数量变化', '期末持股-数量变化比例', '期末持股-持股变动', '期末持股-流通市值', '公告日', '公告日后涨跌幅-10个交易日', '公告日后涨跌幅-30个交易日', '公告日后涨跌幅-60个交易日']
    """
    df = ak.stock_gdfx_free_holding_analyse_em(date=date)
    
    return df


@action(name="GetShareholdersHoldingAnalysis")
@handle_large_data()
def stock_gdfx_holding_analyse_em(date: str,
                                  ) -> pd.DataFrame:
    """
    Get the analysis on stock holding of the top 10 shareholders for all A-share stocks on the specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '股票代码', '股票简称', '报告期', '期末持股-数量', '期末持股-数量变化', '期末持股-数量变化比例', '期末持股-持股变动', '期末持股-流通市值', '公告日', '公告日后涨跌幅-10个交易日', '公告日后涨跌幅-30个交易日', '公告日后涨跌幅-60个交易日']
    """
    df = ak.stock_gdfx_holding_analyse_em(date=date)
    
    return df


@action(name="GetTop10CirculatingShareholders")
@handle_large_data()
def stock_gdfx_free_holding_detail_em(date: str,
                                      ) -> pd.DataFrame:
    """
    Get detailed information on stock holding of the top 10 circulating shareholders for a specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '股票代码', '股票简称', '报告期', '期末持股-数量', '期末持股-数量变化', '期末持股-数量变化比例', '期末持股-持股变动', '期末持股-流通市值', '公告日']
    """
    df = ak.stock_gdfx_free_holding_detail_em(date=date)
    
    return df


@action(name="GetTop10ShareholdersInformation")
@handle_large_data()
def stock_gdfx_holding_detail_em(
    date: str, indicator: str = "个人", symbol: str = "新进",
    ) -> pd.DataFrame:
    """
    Get detailed information on stock holding of the top 10 shareholders for a specified date.

    Parameters:
    - date: The date of the financial report release, e.g., "20230331".
    - indicator: The type of shareholder,  choice of {"个人", "基金", "QFII", "社保", "券商", "信托"}.
    - symbol: The holding change symbol, choice of {"新进", "增加", "不变", "减少"}.
    
    Return:
        ['股东名称', '股东排名', '股票代码', '股票简称', '报告期', '期末持股-数量', '期末持股-数量变化', '期末持股-数量变化比例', '期末持股-持股变动', '期末持股-流通市值', '公告日', '股东类型']
    """
    df = ak.stock_gdfx_holding_detail_em(
        date=date, indicator=indicator, symbol=symbol
    )
    
    return df


@action(name="GetTopTenCirculatingShareholdersStatistics")
@handle_large_data()
def stock_gdfx_free_holding_statistics_em(date: str,
                                          ) -> pd.DataFrame:
    """
    Get the statistics on stock holding of the top 10 circulating shareholders for all A-share stocks on the specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '统计次数', '公告日后涨幅统计-10个交易日-平均涨幅', '公告日后涨幅统计-10个交易日-最大涨幅', '公告日后涨幅统计-10个交易日-最小涨幅', '公告日后涨幅统计-30个交易日-平均涨幅', '公告日后涨幅统计-30个交易日-最大涨幅', '公告日后涨幅统计-30个交易日-最小涨幅', '公告日后涨幅统计-60个交易日-平均涨幅', '公告日后涨幅统计-60个交易日-最大涨幅', '公告日后涨幅统计-60个交易日-最小涨幅', '持有个股']
    """
    df = ak.stock_gdfx_free_holding_statistics_em(date=date)
    
    return df


@action(name="GetTopTenShareholdersStatistics")
@handle_large_data()
def stock_gdfx_holding_statistics_em(date: str,
                                     ) -> pd.DataFrame:
    """
    Get the statistics on stock holding of the top 10 shareholders for all A-share stocks on the specified date.

    Parameters:
    - date: Date of the financial report publication quarter's last day (e.g., "20210930")
    
    Return:
        ['股东名称', '股东类型', '统计次数', '公告日后涨幅统计-10个交易日-平均涨幅', '公告日后涨幅统计-10个交易日-最大涨幅', '公告日后涨幅统计-10个交易日-最小涨幅', '公告日后涨幅统计-30个交易日-平均涨幅', '公告日后涨幅统计-30个交易日-最大涨幅', '公告日后涨幅统计-30个交易日-最小涨幅', '公告日后涨幅统计-60个交易日-平均涨幅', '公告日后涨幅统计-60个交易日-最大涨幅', '公告日后涨幅统计-60个交易日-最小涨幅', '持有个股']
    """
    df = ak.stock_gdfx_holding_statistics_em(date=date)
    
    return df


@action(name="GetTopTenShareholdersTeamwork")
@handle_large_data()
def stock_gdfx_free_holding_teamwork_em(symbol: str = "全部",
                                        ) -> pd.DataFrame:
    """
    Get data of the top 10 circulating synergistic shareholders for each shareholder.

    Parameters:
    - symbol: The type of shareholders to focus on, choice of {"全部", "个人", "基金", "QFII", "社保", "券商", "信托"}.
    
    Return:
        ['股东名称', '股东类型', '协同股东名称', '协同股东类型', '协同次数', '个股详情']
    """
    df = ak.stock_gdfx_free_holding_teamwork_em(symbol=symbol)
    
    return df


@action(name="GetTopTenShareholdersTeamwork")
@handle_large_data()
def stock_gdfx_holding_teamwork_em(symbol: str = "全部",
                                   ) -> pd.DataFrame:
    """
    Get data of the top 10 synergistic shareholders for each shareholder.

    Parameters:
    - symbol: The type of shareholders to focus on, choice of {"全部", "个人", "基金", "QFII", "社保", "券商", "信托"}.
    
    Return:
        ['股东名称', '股东类型', '协同股东名称', '协同股东类型', '协同次数', '个股详情']
    """
    df = ak.stock_gdfx_holding_teamwork_em(symbol=symbol)
    
    return df


@action(name="GetShareholdersDetail")
@handle_large_data()
def stock_zh_a_gdhs_detail_em(symbol: str,
                              ) -> pd.DataFrame:
    """
    Get details on the number changes of shareholders for a specified A-share stock.

    Parameters:
    - symbol: The stock ticker, e.g., "000001".
    
    Return:
        ['股东户数统计截止日', '区间涨跌幅', '股东户数-本次', '股东户数-上次', '股东户数-增减', '股东户数-增减比例', '户均持股市值', '户均持股数量', '总市值', '总股本', '股本变动', '股本变动原因', '股东户数公告日期', '代码','名称']
    """
    df = ak.stock_zh_a_gdhs_detail_em(symbol=symbol)
    
    return df


@action(name="GetMajorShareholders")
@handle_large_data()
def stock_main_stock_holder(stock,
                            ) -> pd.DataFrame:
    """
    Get information of major shareholders of a specific stock.

    Parameters:
    - stock (str): The stock ticker.
    
    Return:
        ['股东名称', '持股数量', '持股比例', '股本性质', '截至日期', '公告日期', '股东说明', '股东总数', '平均持股数']
    """
    df = ak.stock_main_stock_holder(stock=stock)
    
    return df


@action(name="GetSSEShareholdingChanges")
@handle_large_data()
def stock_share_hold_change_sse(symbol: str,
                                ) -> pd.DataFrame:
    """
    Get data of changes in shareholdings of directors, supervisors, and senior management personnel in a specified Shanghai Stock Exchange stock.

    Parameters:
    - symbol (str): The stock ticker symbol of SSE. e.g. '600000'
    
    Return:
        ['公司代码', '公司名称', '姓名', '职务', '股票种类', '货币种类', '本次变动前持股数', '变动数', '本次变动平均价格', '变动后持股数', '变动原因', '变动日期', '填报日期']
    """
    df = ak.stock_share_hold_change_sse(
        symbol=symbol)
    
    return df


@action(name="GetSZSEShareholdingChanges")
@handle_large_data()
def stock_share_hold_change_szse(symbol: str,
                                 ) -> pd.DataFrame:
    """
    Get data of changes in shareholdings of directors, supervisors, and senior management personnel in a specified Shenzhen Stock Exchange stock.

    Parameters:
    - symbol (str): The stock ticker symbol of SZSE. e.g. '001308'
    
    Return:
        ['证券代码', '证券简称', '董监高姓名', '变动日期', '变动股份数量', '成交均价', '变动原因', '变动比例', '当日结存股数', '股份变动人姓名', '职务', '变动人与董监高的关系']
    """
    df = ak.stock_share_hold_change_szse(
        symbol=symbol)
    
    return df


@action(name="GetBSEShareholdingChanges")
@handle_large_data()
def stock_share_hold_change_bse(symbol: str,
                                ) -> pd.DataFrame:
    """
    Get data of changes in shareholdings of directors, supervisors, and senior management personnel in a specified Beijing Stock Exchange stock.

    Parameters:
    - symbol (str): The stock ticker symbol of BSE. e.g. '430489'.
    
    Return:
        ['代码', '简称', '姓名', '职务', '变动日期', '变动股数', '变动前持股数', '变动后持股数', '变动均价', '变动原因']
    """
    df = ak.stock_share_hold_change_bse(
        symbol=symbol)
    
    return df


@action(name="GetShareholderNumAndConcentration")
@handle_large_data()
def stock_hold_num_cninfo(date: str,
                          ) -> pd.DataFrame:
    """
    Get data on the number of shareholders and the concentration of shareholdings for all A-share stocks on a specified date.

    Parameters:
    - date (str): The specified date. Choose from {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"};
                    starting from "20170331".
    
    Return:
        ['证劵代码', '证券简称', '变动日期', '本期股东人数', '上期股东人数', '股东人数增幅', '本期人均持股数量', '上期人均持股数量', '人均持股数量增幅']
    """
    df = ak.stock_hold_num_cninfo(date=date)
    
    return df


@action(name="GetActualControllerHoldChange")
@handle_large_data()
def stock_hold_control_cninfo(symbol: str = "单独控制",
                              ) -> pd.DataFrame:
    """
    Get data on the changes in shareholding of the actual controller from the special statistics section.

    Parameters:
    - symbol (str): The specified symbol. Choose from {"单独控制", "实际控制人",
                      "一致行动人", "家族控制", "全部"}; starting from "2010".
    
    Return:
        ['证劵代码', '证券简称', '变动日期', '实际控制人名称', '控股数量', '控股比例', '直接控制人名称', '控制类型']
    """
    df = ak.stock_hold_control_cninfo(symbol=symbol)
    
    return df


@action(name="GetSeniorManagementHoldDetail")
@handle_large_data()
def stock_hold_management_detail_cninfo(symbol: str = "增持",
                                        ) -> pd.DataFrame:
    """
    Get detailed data on changes in senior executives' shareholdings for all A-share stocks.

    Parameters:
    - symbol (str): The specified symbol. Choose from {"增持", "减持"}.
    
    Return:
        ['证劵代码', '证券简称', '截止日期', '公告日期', '高管姓名', '董监高姓名', '董监高职务', '变动人与董监高关系', '期初持股数量', '期末持股数量', '变动数量', '变动比例', '成交均价', '期末市值', '持股变动原因', '数据来源']
    """
    df = ak.stock_hold_management_detail_cninfo(
        symbol=symbol
    )
    
    return df


@action(name="GetSeniorManagementHoldDetail2")
@handle_large_data()
def stock_hold_management_detail_em() -> pd.DataFrame:
    """
    Get historical detailed data on shareholding changes of directors, supervisors, senior executives, and related personnel for all A-share stocks.
    
    Return:
        ['日期', '代码', '名称', '变动人', '变动股数', '成交均价', '变动金额', '变动原因', '变动比例', '变动后持股数', '持股种类', '董监高人员姓名', '职务', '变动人与董监高的关系', '开始时持有', '结束后持有']
    """
    df = ak.stock_hold_management_detail_em()
    
    return df


@action(name="GetPersonnelHoldDetail")
@handle_large_data()
def stock_hold_management_person_em(symbol: str, name: str,
                                    ) -> pd.DataFrame:
    """
    Get detailed information on the increase or decrease in shareholdings by a specific executive in a specific stock.

    Parameters:
    - symbol (str): The stock code. e.g. '001308'
    - name (str): The name of the personnel. e.g. '孙建华'
    
    Return:
        ['日期', '代码', '名称', '变动人', '变动股数', '成交均价', '变动金额', '变动原因', '变动比例', '变动后持股数', '持股种类', '董监高人员姓名', '职务', '变动人与董监高的关系', '开始时持有', '结束后持有']
    """
    df = ak.stock_hold_management_person_em(
        symbol=symbol, name=name
    )
    
    return df

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetAllStockFundFlow")
@handle_large_data()
def stock_fund_flow_individual(symbol: str,
                               ) -> pd.DataFrame:
    """
    Get fund flow ranking data for all A-share stocks during a specified time period.

    Parameters:
    - symbol: Timeframe for the fund flow data. Choices are "即时" (real-time), "3日排行" (3-day ranking),
                   "5日排行" (5-day ranking), "10日排行" (10-day ranking), "20日排行" (20-day ranking).
    
    Return:
        ['股票代码', '股票简称', '最新价', '涨跌幅', '换手率', '流入资金', '流出资金', '净额', '成交额', '大单流入']
    """
    df = ak.stock_fund_flow_individual(symbol=symbol)
    
    return df


@action(name="GetConceptStockFundFlow")
@handle_large_data()
def stock_fund_flow_concept(symbol: str,
                            ) -> pd.DataFrame:
    """
    Get concept fund flow ranking data for A-shares during a specified time period.

    Parameters:
    - symbol: Timeframe for the fund flow data. Choices are "即时" (real-time), "3日排行" (3-day ranking),
                   "5日排行" (5-day ranking), "10日排行" (10-day ranking), "20日排行" (20-day ranking).
    
    Return:
        ['行业', '行业指数', '行业-涨跌幅', '流入资金', '流出资金', '净额', '公司家数', '领涨股', '领涨股-涨跌幅', '当前价']
    """
    df = ak.stock_fund_flow_concept(symbol=symbol)
    
    return df


@action(name="GetIndustryStockFundFlow")
@handle_large_data()
def stock_fund_flow_industry(symbol: str,
                             ) -> pd.DataFrame:
    """
    Get industry fund flow ranking data for A-shares during a specified time period.

    Parameters:
    - symbol: Timeframe for the fund flow data. Choices are "即时" (real-time), "3日排行" (3-day ranking),
                   "5日排行" (5-day ranking), "10日排行" (10-day ranking), "20日排行" (20-day ranking).
    
    Return:
        ['行业', '行业指数', '行业-涨跌幅', '流入资金', '流出资金', '净额', '公司家数', '领涨股', '领涨股-涨跌幅', '当前价']
    """
    df = ak.stock_fund_flow_industry(symbol=symbol)
    
    return df


@action(name="GetBigDealTracking")
@handle_large_data()
def stock_fund_flow_big_deal() -> pd.DataFrame:
    """
    Get real-time large order tracking data for all A-shares.
    
    Return:
        ['成交时间', '股票代码', '股票简称', '成交价格', '成交量', '成交额', '大单性质', '涨跌幅', '涨跌额']
    """
    df = ak.stock_fund_flow_big_deal()
    
    return df


@action(name="GetIndividualFundFlow")
@handle_large_data()
def stock_individual_fund_flow(stock: str, market: str = "sh",
                               ) -> pd.DataFrame:
    """
    Get the fund flow data for a specified A-share stock over the past 100 trading days.
    
    Parameters:
    - stock: Ticker symbol of specific stock.
    - market: Market of the stock. Choices: {"sh", "sz", "bj"} stands for 'Shanghai Stock Exchange', 'Shenzhen Stock Exchange' and 'Beijing Stock Exchange' respectively.
    
    Return:
        ['日期', '收盘价', '涨跌幅', '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比']
    """
    df = ak.stock_individual_fund_flow(stock=stock, market=market)
    
    return df


@action(name="GetStockFundFlowRankings")
@handle_large_data()
def stock_individual_fund_flow_rank(indicator: str,
                                    ) -> pd.DataFrame:
    """
    Get the individual stock fund flow ranking data for A-shares during a specified period.

    Parameters:
    - indicator: The period indicator, e.g., "今日" (today), "3日" (3 days), "5日" (5 days), "10日" (10 days).
    
    Returns:
        ['代码', '名称', '最新价', '今日涨跌幅', '今日主力净流入-净额', '今日主力净流入-净占比', '今日超大单净流入-净额', '今日超大单净流入-净占比', '今日大单净流入-净额', '今日大单净流入-净占比', '今日中单净流入-净额', '今日中单净流入-净占比', '今日小单净流入-净额', '今日小单净流入-净占比']
    """
    df = ak.stock_individual_fund_flow_rank(indicator=indicator)
    
    return df


@action(name="GetMarketFundFlow")
@handle_large_data()
def stock_market_fund_flow() -> pd.DataFrame:
    """
    Get the historical fund/capital flow data of the A-share major market indexes.
    
    Returns:
        ['日期', '上证-收盘价', '上证-涨跌幅', '深证-收盘价', '深证-涨跌幅', '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比']
    """
    df = ak.stock_market_fund_flow()
    
    return df


@action(name="GetSectorFundFlowRank")
@handle_large_data()
def stock_sector_fund_flow_rank(indicator: str = "今日", sector_type: str = "行业资金流",
                                ) -> pd.DataFrame:
    """
    Get the fund flow ranking data for industry, concept, and regional fund flows within a specified period.

    Parameters:
    - indicator: The time period indicator, choice of {"今日", "5日", "10日"}. e.g., "5日",
    - sector_type: The type of sector, choice of {"行业资金流", "概念资金流", "地域资金流"}. e.g., "行业资金流" for industry fund flow.
    
    Return:
        ['名称', '今日涨跌幅', '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比', '主力净流入最大股']
    """
    df = ak.stock_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)
    
    return df


@action(name="GetSectorFundFlowSummary")
@handle_large_data()
def stock_sector_fund_flow_summary(symbol: str, indicator: str = "今日",
                                   ) -> pd.DataFrame:
    """
    Get the stock fund flows within a specified industry during a specified period.

    Parameters:
    - symbol: The industry sector symbol, choice of {
    "计算机设备", "互联网服务", "软件开发", "石油行业", "煤炭行业",
    "通信服务", "半导体", "电子元件", "橡胶制品", "电子化学品",
    "家电行业", "仪器仪表", "航运港口", "公用事业", "教育",
    "包装材料", "燃气", "农药兽药", "工程咨询服务", "采掘行业",
    "综合行业", "农牧饲渔", "电力行业", "医药商业", "汽车服务",
    "铁路公路", "家用轻工", "玻璃玻纤", "电源设备", "风电设备",
    "医疗器械", "化纤行业", "交运设备", "房地产服务", "钢铁行业",
    "塑料制品", "航天航空", "装修装饰", "商业百货", "专业服务",
    "非金属材料", "小金属", "贵金属", "电机", "化肥行业",
    "环保行业", "生物制品", "通用设备", "水泥建材", "物流行业", "化学原料",
    "纺织服装", "造纸印刷", "贸易行业", "有色金属",
    "航空机场", "中药", "装修建材", "工程建设", "船舶制造",
    "旅游酒店", "专用设备", "美容护理", "工程机械", "食品饮料",
    "游戏", "化学制品", "保险", "多元金融", "文化传媒",
    "化学制药", "珠宝首饰", "光学光电子", "房地产开发", "电网设备",
    "证券", "消费电子", "光伏设备", "医疗服务", "能源金属",
    "通信设备", "汽车零部件", "银行", "酿酒行业", "汽车整车",
    "电池"}. e.g., "电源设备".
    - indicator: The time period indicator, choice of {"今日", "5日", "10日"}. e.g., "今日".
    
    Return:
        ['代码', '名称', '最新价', '今日涨跌幅', '今日主力净流入-净额', '今日主力净流入-净占比', '今日超大单净流入-净额', '今日超大单净流入-净占比', '今日大单净流入-净额', '今日大单净流入-净占比', '今日中单净流入-净额', '今日中单净流入-净占比', '今日小单净流入-净额', '今日小单净流入-净占比']
    """
    df = ak.stock_sector_fund_flow_summary(symbol=symbol, indicator=indicator)
    
    return df


@action(name="GetSectorFundFlowHist")
@handle_large_data()
def stock_sector_fund_flow_hist(symbol: str,
                                ) -> pd.DataFrame:
    """
    Get historical fund flow data for a specified industry.

    Parameters:
    - symbol: The industry sector symbol, choice of {
    "计算机设备", "互联网服务", "软件开发", "石油行业", "煤炭行业",
    "通信服务", "半导体", "电子元件", "橡胶制品", "电子化学品",
    "家电行业", "仪器仪表", "航运港口", "公用事业", "教育",
    "包装材料", "燃气", "农药兽药", "工程咨询服务", "采掘行业",
    "综合行业", "农牧饲渔", "电力行业", "医药商业", "汽车服务",
    "铁路公路", "家用轻工", "玻璃玻纤", "电源设备", "风电设备",
    "医疗器械", "化纤行业", "交运设备", "房地产服务", "钢铁行业",
    "塑料制品", "航天航空", "装修装饰", "商业百货", "专业服务",
    "非金属材料", "小金属", "贵金属", "电机", "化肥行业",
    "环保行业", "生物制品", "通用设备", "水泥建材", "物流行业", "化学原料",
    "纺织服装", "造纸印刷", "贸易行业", "有色金属",
    "航空机场", "中药", "装修建材", "工程建设", "船舶制造",
    "旅游酒店", "专用设备", "美容护理", "工程机械", "食品饮料",
    "游戏", "化学制品", "保险", "多元金融", "文化传媒",
    "化学制药", "珠宝首饰", "光学光电子", "房地产开发", "电网设备",
    "证券", "消费电子", "光伏设备", "医疗服务", "能源金属",
    "通信设备", "汽车零部件", "银行", "酿酒行业", "汽车整车",
    "电池"}. e.g., "电源设备".
    
    Return:
        ['日期', '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比']
    """
    df = ak.stock_sector_fund_flow_hist(symbol=symbol)
    
    return df


@action(name="GetConceptFundFlowHist")
@handle_large_data()
def stock_concept_fund_flow_hist(symbol: str,
                                 ) -> pd.DataFrame:
    """
    Obtain recent historical fund flow data for a specified concept sector.

    Parameters:
    - symbol: The concept sector symbol in chinese, e.g., "锂电池", "数据中心", "智慧城市", "网络安全", "大数据", "边缘计算", "国产芯片"....
    
    Return:
        ['日期', '主力净流入-净额', '主力净流入-净占比', '超大单净流入-净额', '超大单净流入-净占比', '大单净流入-净额', '大单净流入-净占比', '中单净流入-净额', '中单净流入-净占比', '小单净流入-净额', '小单净流入-净占比']
    """
    df = ak.stock_concept_fund_flow_hist(symbol=symbol)
    
    return df
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler import datetime_utils
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetIndustryConstituentStocks")
@handle_large_data()
def stock_board_industry_cons_ths(symbol: str,
                                  ) -> pd.DataFrame:
    """
    Get real-time market data for constituent stocks of a specified industry in A-shares.

    Parameters:
    - symbol: Industry sector symbol. Choice of {
    "半导体及元件", "白色家电", "房地产服务", "房地产开发",
    "化工合成材料", "互联网电商", "家用轻工", "建筑材料", "建筑装饰",
    "零售", "美容护理", "煤炭开采加工", "贸易", "农产品加工", "农业服务",
    "其他电子", "其他社会服务", "燃气", "汽车服务", "汽车零部件",
    "汽车整车物流消费电子", "小家电", "小金属种植业与林业", "医疗服务",
    "医疗器械", "饮料制造", "专用设备", "造纸", "保险及其他",
    "非金属材料", "黑色家电", "包装印刷", "传媒", "厨卫电器",
    "电力", "非汽车交运", "服装家纺", "纺织制造", "化学原料",
    "化学制品", "化学制药", "电力设备", "电子化学品", "国防军工",
    "贵金属", "港口航运", "公路铁路运输", "钢铁", "光学光电子",
    "工业金属", "环保", "机场航运", "酒店及餐饮", "景点及旅游",
    "计算机设备", "计算机应用", "金属新材料", "教育", "食品加工制造",
    "生物制品", "石油加工贸易", "通信服务", "通信设备", "通用设备",
    "油气开采及服务", "仪器仪表", "银行", "医药商业", "养殖业",
    "自动化设备", "综合", "证券", "中药"}.
        e.g. '半导体及元件'
        
    Return:
        ['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率']
    """
    df = ak.stock_board_industry_cons_ths(symbol=symbol)
    
    return df


@action(name="GetIndustrySummary")
@handle_large_data()
def stock_board_industry_summary_ths() -> pd.DataFrame:
    """
    Get real-time market data for each industry in the A-share market.
    
    Return:
        ['序号', '板块', '涨跌幅', '总成交量', '总成交额', '净流入', '上涨家数', '下跌家数', '均价', '领涨股', '领涨股-最新价', '领涨股-涨跌幅']
    """
    df = ak.stock_board_industry_summary_ths()
    
    return df


@action(name="GetIndustryIndexData")
@handle_large_data()
def stock_board_industry_index_ths(
    symbol: str, start_date: str = "19000101", end_date: str = datetime_utils.yyyymmdd(),
    ) -> pd.DataFrame:
    """
    Get daily quote data for a specified industry in the A-share market within a specified time range.

    Parameters:
    - symbol: Industry sector symbol. Choice of {
    "半导体及元件", "白色家电", "房地产服务", "房地产开发",
    "化工合成材料", "互联网电商", "家用轻工", "建筑材料", "建筑装饰",
    "零售", "美容护理", "煤炭开采加工", "贸易", "农产品加工", "农业服务",
    "其他电子", "其他社会服务", "燃气", "汽车服务", "汽车零部件",
    "汽车整车物流消费电子", "小家电", "小金属种植业与林业", "医疗服务",
    "医疗器械", "饮料制造", "专用设备", "造纸", "保险及其他",
    "非金属材料", "黑色家电", "包装印刷", "传媒", "厨卫电器",
    "电力", "非汽车交运", "服装家纺", "纺织制造", "化学原料",
    "化学制品", "化学制药", "电力设备", "电子化学品", "国防军工",
    "贵金属", "港口航运", "公路铁路运输", "钢铁", "光学光电子",
    "工业金属", "环保", "机场航运", "酒店及餐饮", "景点及旅游",
    "计算机设备", "计算机应用", "金属新材料", "教育", "食品加工制造",
    "生物制品", "石油加工贸易", "通信服务", "通信设备", "通用设备",
    "油气开采及服务", "仪器仪表", "银行", "医药商业", "养殖业",
    "自动化设备", "综合", "证券", "中药"}.
        e.g. '半导体及元件'.
    - start_date: Start date in the format "YYYYMMDD".
    - end_date: End date in the format "YYYYMMDD".
    
    Return:
        ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']
    """
    df = ak.stock_board_industry_index_ths(
        symbol=symbol, start_date=start_date, end_date=end_date
    )
    
    return df


@action(name="GetIndustrySectorData")
@handle_large_data()
def stock_board_industry_name_em() -> pd.DataFrame:
    """
    Get real-time market statistics for all industry sectors in the A-share market.
    
    Return:
        ['排名', '板块名称', '板块代码', '最新价', '涨跌额', '涨跌幅', '总市值', '换手率', '上涨家数', '下跌家数', '领涨股票', '领涨股票-涨跌幅']
    """
    df = ak.stock_board_industry_name_em()
    
    return df
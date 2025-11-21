import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetUnusualTradingData")
@handle_large_data()
def stock_changes_em(symbol: str = "大笔买入",
                     ) -> pd.DataFrame:
    """
    Get the latest trading day's market anomaly data for a specified type of anomaly.

    Parameters:
    - symbol: The type of abnormal trading, e.g., "大笔买入". Choices are {'火箭发射', '快速反弹', '大笔买入', '封涨停板', '打开跌停板', '有大买盘', '竞价上涨', '高开5日线', '向上缺口', '60日新高', '60日大幅上涨', '加速下跌', '高台跳水', '大笔卖出', '封跌停板', '打开涨停板', '有大卖盘', '竞价下跌', '低开5日线', '向下缺口', '60日新低', '60日大幅下跌'}.
    
    Return:
        ['时间', '代码', '名称', '板块', '相关信息']
    """
    return ak.stock_changes_em(symbol=symbol)


@action(name="GetUnusualSectorChanges")
@handle_large_data()
def stock_board_change_em(
        ) -> pd.DataFrame:
    """
    Get the details of sector anomalies for the latest trading day.
    
    Return:
        ['板块名称', '涨跌幅', '主力净流入', '板块异动总次数', '板块异动最频繁个股及所属类型-股票代码', '板块异动最频繁个股及所属类型-股票名称', '板块异动最频繁个股及所属类型-买卖方向', '板块具体异动类型列表及出现次数']
    """
    return filtered_df

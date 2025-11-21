import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data


@action(name="GetHSGTFundFlowSummary")
@handle_large_data()
def stock_hsgt_fund_flow_summary_em() -> pd.DataFrame:
    """
    Get Shanghai-Hong Kong Stock Connect and Shenzhen-Hong Kong Stock Connect capital flow data.
    
    Return:
        ['交易日', '类型', '板块', '资金方向', '交易状态', '成交净买额', '资金净流入', '当日资金余额', '上涨数', '持平数', '下跌数', '相关指数', '指数涨跌幅']
    """
    return ak.stock_hsgt_fund_flow_summary_em()

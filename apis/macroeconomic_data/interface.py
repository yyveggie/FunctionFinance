import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from data_connection.data_handler import handle_large_data
from actionweaver import action
import akshare as ak
import pandas as pd
from crawler import datetime_utils
from typing import List, Optional, Any

# 中国宏观杠杆率
@action(name="Get_China_Macro_Leverage_Ratio")
@handle_large_data()
def macro_cnbs(
    condition_column: Optional[str] = None,
    specific_value: Any = None,
    target_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Return macro leverage ratio data for China annually.
    
    Parameters type 2(Accessible only to No.2 agent):
    - condition_column: str — The column name to filter rows by. Defaults to selecting all rows if None.
    - specific_value — The specific value in the condition column to filter by. Used only if condition_column is not None.
    - target_columns: list — The list of columns to select. Defaults to all columns if None.
    """
    df = ak.macro_cnbs()
    if condition_column is not None and specific_value is not None:
        try:
            condition = df[condition_column] == specific_value
            filtered_df = df.loc[condition]
        except Exception as e:
            filtered_df = df
    else:
        filtered_df = df

    if target_columns is not None:
        try:
            filtered_df = filtered_df[target_columns]
        except Exception as e:
            filtered_df = filtered_df
    return filtered_df

# 企业商品价格指数
@action(name="Get_China_Enterprise_Commodity_Price_Index")
@handle_large_data()
def macro_china_qyspjg(
    condition_column: Optional[str] = None,
    specific_value: Any = None,
    target_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Return to China Historical Enterprise Commodity Price Index.
    
    Parameters type 2(Accessible only to No.2 agent):
    - condition_column: str — The column name to filter rows by. Defaults to selecting all rows if None.
    - specific_value — The specific value in the condition column to filter by. Used only if condition_column is not None.
    - target_columns: list — The list of columns to select. Defaults to all columns if None.
    """
    df = ak.macro_china_qyspjg()
    if condition_column is not None and specific_value is not None:
        try:
            condition = df[condition_column] == specific_value
            filtered_df = df.loc[condition]
        except Exception as e:
            filtered_df = df
    else:
        filtered_df = df

    if target_columns is not None:
        try:
            filtered_df = filtered_df[target_columns]
        except Exception as e:
            filtered_df = filtered_df
    return filtered_df

print(macro_china_qyspjg())

# 外商直接投资数据
@action(name="Get_China_Foreign_direct_investment_data")
@handle_large_data()
def macro_china_fdi(
    condition_column: Optional[str] = None,
    specific_value: Any = None,
    target_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Returns all historical foreign direct investment data in China.
    
    Parameters type 2(Accessible only to No.2 agent):
    - condition_column: str — The column name to filter rows by. Defaults to selecting all rows if None.
    - specific_value — The specific value in the condition column to filter by. Used only if condition_column is not None.
    - target_columns: list — The list of columns to select. Defaults to all columns if None.
    """
    df = ak.macro_china_fdi()
    if condition_column is not None and specific_value is not None:
        try:
            condition = df[condition_column] == specific_value
            filtered_df = df.loc[condition]
        except Exception as e:
            filtered_df = df
    else:
        filtered_df = df

    if target_columns is not None:
        try:
            filtered_df = filtered_df[target_columns]
        except Exception as e:
            filtered_df = filtered_df
    return filtered_df

# LPR品种数据
@action(name="Get_China_LPR_variety_data")
@handle_large_data()
def macro_china_lpr(
    condition_column: Optional[str] = None,
    specific_value: Any = None,
    target_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Return all historical LPR variety data in China.
    
    Parameters type 2(Accessible only to No.2 agent):
    - condition_column: str — The column name to filter rows by. Defaults to selecting all rows if None.
    - specific_value — The specific value in the condition column to filter by. Used only if condition_column is not None.
    - target_columns: list — The list of columns to select. Defaults to all columns if None.
    """
    df = ak.macro_china_lpr()
    if condition_column is not None and specific_value is not None:
        try:
            condition = df[condition_column] == specific_value
            filtered_df = df.loc[condition]
        except Exception as e:
            filtered_df = df
    else:
        filtered_df = df

    if target_columns is not None:
        try:
            filtered_df = filtered_df[target_columns]
        except Exception as e:
            filtered_df = filtered_df
    return filtered_df


print(macro_china_lpr())
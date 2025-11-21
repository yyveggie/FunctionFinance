import akshare as ak
import json
import os
import pandas as pd
from datetime import datetime
from pymongo import MongoClient # 导入MongoClient
import logging # 导入日志库

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
函数功能：获取指定股票在特定时间段的历史价格数据并保存到MongoDB数据库
参数说明：
    stocks_file: 股票代码配置文件路径
    start_date: 开始日期，格式为'YYYY-MM-DD'
    end_date: 结束日期，格式为'YYYY-MM-DD'
    mongo_uri: MongoDB 连接字符串
    db_name: 数据库名称
    source_value: 来源标识
"""
def fetch_stock_data(stocks_file="stocks_en.json", start_date=None, end_date=None, mongo_uri="mongodb://localhost:27017/", db_name="Quote", source_value="finance.sina.com"):
    # 连接MongoDB
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        logging.info(f"成功连接到 MongoDB: {mongo_uri}, 数据库: {db_name}")
    except Exception as e:
        logging.error(f"连接 MongoDB 失败: {e}")
        return

    # 读取股票列表
    try:
        with open(stocks_file, 'r') as f:
            stocks_config = json.load(f)
        stocks_list = json.loads(stocks_config["stocks"])
    except FileNotFoundError:
        logging.error(f"股票配置文件 {stocks_file} 未找到。")
        client.close()
        return
    except json.JSONDecodeError:
        logging.error(f"解析股票配置文件 {stocks_file} 失败。")
        client.close()
        return
    except Exception as e:
        logging.error(f"读取或解析股票配置文件时发生错误: {e}")
        client.close()
        return

    # 循环处理每个股票
    for stock in stocks_list:
        logging.info(f"正在获取 {stock} 的历史数据...")

        try:
            # 获取股票数据
            stock_data_df = ak.stock_us_daily(symbol=stock, adjust="")

            # 确保返回的是DataFrame
            if not isinstance(stock_data_df, pd.DataFrame) or stock_data_df.empty:
                logging.warning(f"未能获取或获取到空的 {stock} 数据。")
                continue

            # akshare 返回的 date 列已经是字符串格式 'YYYY-MM-DD'，可以直接使用
            # 如果需要转换为 datetime 对象，取消下面注释
            # stock_data_df['date'] = pd.to_datetime(stock_data_df['date'])

            # 如果提供了日期范围，筛选数据
            if start_date and end_date:
                try:
                    # 筛选前确保日期列是可比较的（字符串格式 YYYY-MM-DD 可以直接比较）
                    stock_data_df = stock_data_df[(stock_data_df['date'] >= start_date) & (stock_data_df['date'] <= end_date)]
                except Exception as e:
                    logging.error(f"筛选 {stock} 日期范围时出错: {e}")
                    continue # 跳过这个股票的处理

            if stock_data_df.empty:
                 logging.info(f"{stock} 在指定日期范围 {start_date} - {end_date} 内没有数据。")
                 continue

            # 准备插入MongoDB的数据
            # 将DataFrame转换为字典列表
            data_to_insert = stock_data_df.to_dict('records')

            # 添加 source 字段
            for record in data_to_insert:
                record['source'] = source_value

            # 获取对应的 collection
            collection = db[stock]

            # 插入数据
            if data_to_insert:
                try:
                    collection.insert_many(data_to_insert)
                    logging.info(f"{stock} 数据（{len(data_to_insert)}条记录）已成功保存到 MongoDB 数据库 '{db_name}' 的 '{stock}' 集合中。")
                except Exception as e:
                    logging.error(f"向 MongoDB 插入 {stock} 数据时出错: {e}")
            else:
                logging.info(f"没有为 {stock} 准备好可插入的数据。")

        except Exception as e:
            logging.error(f"处理 {stock} 数据时发生错误: {e}")
            continue # 继续处理下一个股票

    # 关闭MongoDB连接
    client.close()
    logging.info("所有数据处理完成，已关闭 MongoDB 连接。")

# 示例使用
if __name__ == "__main__":
    # 不指定日期范围，获取所有历史数据并存入MongoDB
    # fetch_stock_data()

    # 指定日期范围，获取特定时间段的数据并存入MongoDB
    fetch_stock_data(start_date="2025-01-01", end_date="2025-04-01")
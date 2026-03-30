import akshare as ak
import argparse
from datetime import date, datetime
from pymongo import MongoClient
import logging # 导入日志库

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().lower()
    if symbol.startswith("sh") or symbol.startswith("sz"):
        return symbol
    if symbol.startswith(("6", "9")):
        return f"sh{symbol}"
    return f"sz{symbol}"


def fetch_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str = "hfq",
    save_to_mongo: bool = True,
    mongo_uri: str = "mongodb://localhost:27017/",
    db_name: str = "Quote",
    collection_name: str = "",
):
    def normalize_for_mongo(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value

    normalized_symbol = normalize_symbol(symbol)
    logging.info(f"正在获取 {normalized_symbol} 的历史数据...")

    stock_df = ak.stock_zh_a_daily(
        symbol=normalized_symbol,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )

    print(stock_df)

    if save_to_mongo:
        final_collection = collection_name.strip() if collection_name and collection_name.strip() else normalized_symbol
        try:
            client = MongoClient(mongo_uri)
            db = client[db_name]
            collection = db[final_collection]

            data_to_insert = stock_df.to_dict("records")
            data_to_insert = [
                {k: normalize_for_mongo(v) for k, v in row.items()} for row in data_to_insert
            ]
            if data_to_insert:
                collection.insert_many(data_to_insert)
                logging.info(f"已写入 MongoDB: {db_name}.{final_collection}, 共 {len(data_to_insert)} 条")
            else:
                logging.warning("没有可写入 MongoDB 的数据")
            client.close()
        except Exception as e:
            logging.error(f"写入 MongoDB 失败: {e}")

# 示例使用
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取中国股票在特定时间段的日线，直接输出并写入 MongoDB")
    parser.add_argument(
        "--symbol",
        type=str,
        nargs="+",
        required=True,
        help="股票代码，支持单个或多个（逗号分隔或空格分隔），如 601919 或 601919,600150"
    )
    parser.add_argument("--start-date", type=str, required=True, help="开始日期，格式 YYYYMMDD")
    parser.add_argument("--end-date", type=str, required=True, help="结束日期，格式 YYYYMMDD")
    parser.add_argument("--adjust", type=str, default="hfq", choices=["", "qfq", "hfq"], help="复权类型: '' | qfq | hfq")
    parser.add_argument("--mongo-uri", type=str, default="mongodb://localhost:27017/", help="MongoDB 连接字符串")
    parser.add_argument("--db-name", type=str, default="Quote", help="MongoDB 数据库名称")
    parser.add_argument("--collection", type=str, default="", help="集合名，默认使用股票代码（如 sh601919）")
    parser.add_argument("--no-save", action="store_true", help="只输出，不写入 MongoDB")

    args = parser.parse_args()

    # 兼容以下输入形式：
    # 1) --symbol 601919,600150
    # 2) --symbol 601919, 600150
    # 3) --symbol SH601919, SH600150 ...
    symbol_text = " ".join(args.symbol)
    symbols = [s.strip() for s in symbol_text.split(",") if s.strip()]
    if not symbols:
        logging.error("未提供有效股票代码")
        raise SystemExit(1)

    for symbol in symbols:
        fetch_stock_data(
            symbol=symbol,
            start_date=args.start_date,
            end_date=args.end_date,
            adjust=args.adjust,
            save_to_mongo=not args.no_save,
            mongo_uri=args.mongo_uri,
            db_name=args.db_name,
            collection_name=args.collection,
        )
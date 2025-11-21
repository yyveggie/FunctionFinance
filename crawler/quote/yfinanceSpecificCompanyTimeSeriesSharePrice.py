import json
import os # 导入 os 模块以处理路径
import asyncio
import rootutils

if __name__ == "__main__":
    # !!! 重要提醒: 下面的日期范围 (2025-01-01 到 2025-04-01) 是未来的日期。 !!!
    # !!! yfinance 无法获取未来数据，预期对每个 ticker 都会获取失败。      !!!
    # !!! 如果需要获取历史数据，请修改为过去的日期范围。                   !!!
    start_date = '2025-01-01'
    end_date = '2025-04-01'

    # 假设 ticker_codes.json 在项目根目录下
    # rootutils 应该已经将根目录设置为工作目录或添加到 pythonpath
    # 尝试直接使用相对路径，如果不行，可能需要更精确的路径构建
    # 或者，我们可以从 rootutils 获取根路径
    project_root = rootutils.find_root(indicator=".project-root")
    json_file_path = os.path.join(project_root, 'ticker_codes.json')

    try:
        with open(json_file_path, 'r') as f:
            ticker_list = json.load(f)
            # 假设 JSON 文件是一个包含股票代码字符串的列表
            if not isinstance(ticker_list, list):
                print(f"错误: {json_file_path} 的内容不是一个有效的列表。")
                ticker_list = [] # 置空列表以防止后续错误

    except FileNotFoundError:
        print(f"错误: 未在项目根目录找到 {json_file_path} 文件。")
        ticker_list = []
    except json.JSONDecodeError:
        print(f"错误: 解析 {json_file_path} 文件时出错，请检查其 JSON 格式。")
        ticker_list = []
    except Exception as e:
        print(f"读取 {json_file_path} 时发生未知错误: {e}")
        ticker_list = []


    print(f"将尝试为以下股票代码获取 {start_date} 到 {end_date} 的数据 (预期失败):")
    print(ticker_list)

    # 循环处理列表中的每个股票代码
    for ticker in ticker_list:
        if isinstance(ticker, str) and ticker: # 确保 ticker 是非空字符串
            print(f"--- 开始处理: {ticker} ---")
            try:
                result = asyncio.run(main(ticker, start_date, end_date))
                if result:
                    # 通常这里会是空数据，因为日期是未来的
                    print(f"处理 {ticker} 完成。返回的数据: {result.get('data', '无数据')[:5] if result.get('data') else '无数据'}")
                else:
                    # main 函数在出错或无数据时返回 {}
                    print(f"未能获取 {ticker} 的数据 (正如预期，因日期为未来)。")
            except Exception as e:
                print(f"处理 {ticker} 时发生错误: {e}")
            print(f"--- 结束处理: {ticker} ---\n")
        else:
            print(f"跳过无效的 ticker: {ticker}")

    print("所有 ticker 处理完毕。")

# 移除之前的单个 ticker 示例
# ticker = 'AAPL'
# start_date = '2023-01-01'
# end_date = '2023-12-31'
# result = asyncio.run(main(ticker, start_date, end_date))
# if result:
#     print(f"获取到的数据样本 (前5条):")
#     if 'data' in result and result['data']:
#          print(result['data'][:5])
#     else:
#         print("未返回有效数据。") 
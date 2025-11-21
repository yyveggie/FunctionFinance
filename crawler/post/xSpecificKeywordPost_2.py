import tweepy
import csv
import time
from datetime import datetime, timedelta, timezone  # 添加 timezone

# 使用 Twitter API V2 的 Bearer Token
BEARER_TOKEN = r'AAAAAAAAAAAAAAAAAAAAANoSpgEAAAAAlPFy6tjZiiGOP8qWX4fA%2FdtLfEI%3DTRiBw8IdAkKmmvSkdvd8B5Xpn7L23KhFdrSZqC8Yy72mYsV93F'

# 使用 Bearer Token 创建 Client 对象
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# 获取当前时间并格式化为 ISO 8601 格式
current_time = datetime.now(timezone.utc).isoformat()  # 使用 UTC 时间

# 设置要搜索的关键词
keyword = 'TESLA'

import tweepy
import csv
import time
from datetime import datetime, timedelta, timezone  # 添加 timezone

# 使用 Twitter API V2 的 Bearer Token
BEARER_TOKEN = r'AAAAAAAAAAAAAAAAAAAAANoSpgEAAAAAlPFy6tjZiiGOP8qWX4fA%2FdtLfEI%3DTRiBw8IdAkKmmvSkdvd8B5Xpn7L23KhFdrSZqC8Yy72mYsV93F'

# 使用 Bearer Token 创建 Client 对象
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# 设置要搜索的关键词
keyword = 'TESLA'

# 设置时间范围:搜索过去7天的推文(Twitter API 限制)
end_time = datetime.now(timezone.utc)  # 当前时间作为结束时间
start_time = end_time - timedelta(days=7)  # 7天前作为开始时间

# 格式化为 ISO 8601 格式
start_time_str = start_time.isoformat()
end_time_str = end_time.isoformat()

print(f"搜索时间范围: {start_time_str} 到 {end_time_str}")
print(f"搜索关键词: {keyword}")

# 打开 CSV 文件并创建 CSV writer 对象
with open('tweets.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入标题行
    writer.writerow(['Date', 'Keyword', 'Tweet'])

    # 使用 Twitter API V2 进行推文查询
    query = f"{keyword} lang:en"
    
    tweet_count = 0
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            print(f"开始获取推文... (尝试 {retry_count + 1}/{max_retries})")
            
            # 使用 Paginator 进行分页查询,每次最多100条
            tweets = tweepy.Paginator(
                client.search_recent_tweets, 
                query=query, 
                start_time=start_time_str, 
                end_time=end_time_str, 
                tweet_fields=["created_at"],
                max_results=10  # 每次请求10条,降低速率限制风险
            ).flatten(limit=100)

            # 写入推文数据到 CSV
            for tweet in tweets:
                writer.writerow([tweet.created_at, keyword, tweet.text])
                tweet_count += 1
                
                # 每处理10条推文休息一下,避免速率限制
                if tweet_count % 10 == 0:
                    print(f"已获取 {tweet_count} 条推文...")
                    time.sleep(2)  # 休息2秒
            
            print(f"成功获取 {tweet_count} 条推文")
            break  # 成功完成,退出循环
            
        except tweepy.errors.TooManyRequests as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 15 * 60  # 15分钟
                print(f"速率限制已达到! 等待 {wait_time // 60} 分钟后重试... (尝试 {retry_count}/{max_retries})")
                time.sleep(wait_time)
            else:
                print("已达到最大重试次数,程序退出")
                print(f"已保存 {tweet_count} 条推文到文件")
                raise
        
        except Exception as e:
            print(f"发生错误: {type(e).__name__}: {e}")
            print(f"已保存 {tweet_count} 条推文到文件")
            raise

print(f"数据已成功保存到 'tweets.csv',共 {tweet_count} 条推文")
start_date = current_time
end_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat() + 'Z'  # 结束时间为当前时间的7天后

# 打开 CSV 文件并创建 CSV writer 对象
with open('tweets.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入标题行
    writer.writerow(['Date', 'Keyword', 'Tweet'])

    # 使用 Twitter API V2 进行推文查询
    query = f"{keyword} lang:en"
    tweets = tweepy.Paginator(client.search_recent_tweets, query=query, start_time=start_date, 
                              end_time=end_date, tweet_fields=["created_at"]).flatten(limit=100)

    # 写入推文数据到 CSV，处理速率限制
    for tweet in tweets:
        try:
            writer.writerow([tweet.created_at, keyword, tweet.text])
        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Waiting for 15 minutes...")
            time.sleep(15 * 60)  # 等待15分钟后再继续请求
            # 重试请求
            writer.writerow([tweet.created_at, keyword, tweet.text])

print("数据已成功保存到 'tweets.csv'")
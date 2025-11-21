# filename: xSpecificKeywordPost.py
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from tenacity import retry, wait_fixed, stop_after_attempt
from ntscraper import Nitter
import pandas as pd

from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP


class X_Specific_Keyword_Post(Usable_IP):
    def __init__(self, keyword, args={}):
        super().__init__(args)
        self.keyword = keyword
        self.db_connection = MongoConnection('Post')
        self.source = 'x'
        self.no = 50

        # 明确的实例列表（你也可以替换为你信任的自建实例）
        self.instances = [
            "https://nitter.net",
            "https://nitter.it",
            "https://nitter.privacydev.net",
            "https://nitter.42l.fr"
        ]

        # 跳过实例健康检查，避免“Cannot choose from an empty sequence”
        self.scraper = Nitter(
            log_level=1,
            skip_instance_check=True,
            instances=self.instances
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(8))
    def download(self, mode='term', since=None, until=None, language=None):
        final_rows = []
        last_errors = []

        for inst in self.instances:
            print(f"[INFO] Trying instance: {inst}")
            try:
                res = self.scraper.get_tweets(
                    self.keyword,
                    mode=mode,
                    number=self.no,
                    since=since,
                    until=until,
                    language=language,
                    replies=False,
                    max_retries=5,
                    instance=inst  # 显式实例，避免 None
                )

                tweets = []
                if isinstance(res, dict):
                    tweets = res.get('tweets', []) or []
                elif isinstance(res, list):
                    for r in res:
                        tweets.extend(r.get('tweets', []) or [])

                print(f"[INFO] {inst} returned {len(tweets)} tweets")

                if not tweets:
                    # 空页：记录并换下一个实例
                    last_errors.append(f"Empty result on {inst}")
                    continue

                # 解析
                for t in tweets:
                    stats = t.get('stats', {}) or {}
                    final_rows.append({
                        'text': t.get('text', ''),
                        'date': t.get('date', None),
                        'likes': stats.get('likes', 0),
                        'retweets': stats.get('retweets', 0),
                        'replies': stats.get('replies', 0),
                        'username': t.get('username', None),
                        'tweet_id': t.get('tweetId') or t.get('id') or t.get('tweet_id')
                    })

                # 一旦某实例有数据，就结束轮询；也可继续合并其它实例的数据
                break

            except Exception as e:
                print(f"[WARN] Instance {inst} failed: {e}")
                last_errors.append(f"{inst} -> {e}")
                continue

        if not final_rows:
            # 所有实例都空或失败
            raise RuntimeError(f"No data from all instances. Reasons: {last_errors}")

        df = pd.DataFrame(final_rows, columns=['text','date','likes','retweets','replies','username','tweet_id'])

        self.db_connection.save_data(
            self.keyword, self.source, df.to_dict(orient='records'), ordered=False
        )
        return df


if __name__ == "__main__":
    from config import config
    try:
        c = X_Specific_Keyword_Post(keyword='apple', args=config)

        # 先宽松查询确认基础可用性
        df = c.download(mode='term', since=None, until=None, language=None)
        print(df.head())

        # 如果上一步返回数据，再加时间范围
        if not df.empty:
            df2 = c.download(mode='term', since='2024-08-01', until='2024-08-31', language='en')
            print(df2.head())

    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

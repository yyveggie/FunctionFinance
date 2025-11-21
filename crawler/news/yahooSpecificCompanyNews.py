import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from data_connection.mongodb import MongoConnection
from datetime import datetime, timedelta
from crawler import headless_scrape
import yfinance as yf
import pytz

class Yahoo_Specific_Company_News():
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        ny_tz = pytz.timezone('America/New_York')
        self.start_date = ny_tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
        self.end_date = ny_tz.localize(datetime.strptime(end_date, "%Y-%m-%d"))
        self.db_connection = MongoConnection('News')
        self.source = 'yahoo.com'

    def download(self):
        '''
        :return
        [
            {
                'title':
                'publisher':
                'url':
                'create_time':
                'content':
            }
        ]
        '''
        stock = yf.Ticker(self.ticker)
        news = stock.get_news()
        data_list = []
        ny_tz = pytz.timezone('America/New_York')
        for article in news:
            publish_time = datetime.fromtimestamp(article['providerPublishTime'], tz=ny_tz)
            if self.start_date <= publish_time <= self.end_date:
                url = article['link']
                content = headless_scrape.run_sync(urls=[url])[0]
                news_item = {
                    'title': article['title'],
                    'publisher': article['publisher'],
                    'url': url,
                    'create_time': publish_time,
                    'content': content
                }
                data_list.append(news_item)
        self.db_connection.save_data(self.ticker, self.source, data_list)
        return data_list

def main(ticker, start_date=None, end_date=None):
    """
    获取指定股票在指定时间段内的新闻
    :param ticker: 股票代码
    :param start_date: 开始日期，格式为 'YYYY-MM-DD'
    :param end_date: 结束日期，格式为 'YYYY-MM-DD'
    """
    # 如果没有指定日期，使用默认的昨天到今天
    if start_date is None or end_date is None:
        ny_tz = pytz.timezone('America/New_York')
        ny_now = datetime.now(ny_tz)
        end_date = ny_now.strftime("%Y-%m-%d")
        start_date = (ny_now - timedelta(days=1)).strftime("%Y-%m-%d")
    
    c = Yahoo_Specific_Company_News(ticker=ticker, start_date=start_date, end_date=end_date)
    return c.download()

if __name__ == "__main__":
    from pprint import pprint
    # 示例用法：
    # 方式1：使用默认的时间范围（昨天到今天）
    # pprint(main('AAPL'))
    
    # 方式2：指定时间范围
    pprint(main('AAPL', '2024-12-01', '2024-12-05'))
    
    print("Done!")
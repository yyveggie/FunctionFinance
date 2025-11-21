import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    https://github.com/GeneralMills/pytrends

    类1: 关键词在指定时间范围内的搜索热度。
    类2: 多个关键词随着时间的推移多范围内的搜索热度。
    结果：
    date: 这是日期，表示数据的时间点。
    taiwan: 这是该日期下关键词“taiwan”的搜索热度。这个数字是相对的, 不是绝对搜索量。它表示在给定的时间和地点, 关键词“taiwan”相对于所有搜索的比例。这个数字通常会被归一化, 以便在0到100之间。
    isPartial: 这个字段表示数据是否是不完全的。如果是False, 那么数据应该是完全的。

    类3: 对于关键词的搜索热度在指定时间段内, 各个地区(国家、城市、城区、区域)的排名。
    resolution可以选择的有: CITY/COUNTRY/DMA/REGION

    类4: 与指定关键词相关的时间段内的搜索查询排名。

    类5: 与指定关键词相关的时间段内的搜索话题排名。

    类6: 指定国家的 Google 搜索趋势。

    类7: 指定地区的年度搜索主题排行榜。

    注意：时间跨度应该大点。
'''
from crawler.utils import dict_to_split_dict
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
from datetime import datetime, timedelta
from crawler.utils import extract_top_x_entries_general
from pytrends.request import TrendReq


class Google_Specific_Keyword_Trends(Usable_IP):
    def __init__(self, keyword):
        super().__init__()
        # https://github.com/GeneralMills/pytrends
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.keyword = keyword
        self.country = 'us'
        self.start_date = (datetime.now() - timedelta(days=10)
                           ).strftime('%Y-%m-%d')
        self.end_date = (datetime.now() - timedelta(days=1)
                         ).strftime('%Y-%m-%d')
        self.timeframe = f"{self.start_date} {self.end_date}"
        self.db_connection = MongoConnection('Trend')
        self.source = "google"

    def download(self):
        data = {}
        self.pytrends.build_payload(
            kw_list=[self.keyword], timeframe=self.timeframe)  # type: ignore
        try:
            # SearchInterestTrends
            res = self.pytrends.interest_over_time()
            json_data = res.to_dict(orient='records')
            self.db_connection.save_data(
                "SearchInterestTrends", self.source, json_data)
            data["SearchInterestTrends"] = json_data
        except:
            pass
        # try:
        #     # RegionSearchInterestTrends
        #     res = self.pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
        #     dict_data = res.to_dict(orient='split')
        #     self.db_connection.save_data("RegionSearchInterestTrends", self.source, dict_data)
        #     data["RegionSearchInterestTrends"] = dict_data
        # except:
        #     pass
        try:
            # RelatedQueryTrends
            res = self.pytrends.related_queries()
            self.db_connection.save_data(
                "RelatedQueryTrends", self.source, res)
            data["RelatedQueryTrends"] = res
        except:
            pass
        try:
            # RelatedTopicTrends
            res = self.pytrends.related_topics()
            dict_data = res.to_dict(orient='records')
            self.db_connection.save_data(
                "RelatedTopicTrends", self.source, dict_data)
            data["RelatedTopicTrends"] = extract_top_x_entries_general(
                dict_data, 10)
        except:
            pass
        try:
            # GoogleTrends
            res = self.pytrends.trending_searches()
            dict_data = res.to_dict(orient='records')
            self.db_connection.save_data(
                "GoogleTrends", self.source, dict_data)
            data["GoogleTrends"] = extract_top_x_entries_general(dict_data, 10)
        except:
            pass
        try:
            # GoogleRealTimeTrends
            res = self.pytrends.realtime_trending_searches()
            dict_data = res.to_dict(orient='records')
            self.db_connection.save_data(
                "GoogleRealTimeTrends", self.source, dict_data)
            data["GoogleRealTimeTrends"] = extract_top_x_entries_general(
                dict_data, 10)
        except:
            pass
        data_dict = dict_to_split_dict(data)
        return data_dict


if __name__ == "__main__":
    c = Google_Specific_Keyword_Trends(keyword='chatgpt')
    print(c.download())

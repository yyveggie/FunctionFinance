'''
回报或观点的分散性：研究人员衡量股票回报或分析师观点的分散性或相关性。较低的离散度或较高的相关性可能表明羊群行为。还可以结合分析师评级变化来捕捉市场预期的变化。
'''
import pymongo
import pandas as pd
import json

class DispersionOfOpinion:
    def __init__(self, stock_code):
        self.ticker = stock_code
        # 连接MongoDB
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")

    def _get_data(self):
        # 获取数据库
        db = self.client["Forecast"]
        # 获取集合
        collection = db[self.ticker]
        # 查询文档并提取"Recommendation Trends"字段
        document = collection.find_one({}, {"Recommendation Trends": 1})
        recommendation_trends = document["Recommendation Trends"]
        recommendation_trends_str = recommendation_trends['Recommendation Trends']
        # 将JSON字符串转换为Python列表
        recommendation_trends_list = json.loads(recommendation_trends_str)
        # 将列表转换为Pandas DataFrame
        df = pd.DataFrame(recommendation_trends_list)
        # 将"Rating"列设置为索引
        df.set_index("Rating", inplace=True)
        return df

if __name__ == "__main__":
    stock_code = "AAPL"
    do = DispersionOfOpinion(stock_code=stock_code)
    df = do._get_data()
    print(df)
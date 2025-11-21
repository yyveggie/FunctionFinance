'''
分析指定股票的前N名股东每M%分组的平均持股变化数和变化率。
通过连接MongoDB数据库并查询排序后的股东数据,计算每个股东的持股变化率,
然后按照分组大小对股东进行分组,计算每个分组的平均持股变化数和变化率,最终返回一个包含每个百分比分组结果的字典。
'''
from pymongo import MongoClient

class ShareholderAnalysis:
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['Shareholder']
        self.collection = self.db[stock_code]

    def analyze_top_shareholders(self, num_shareholders=100, group_size=10):
        top_shareholders = self.collection.find().sort('current_shares', -1).limit(num_shareholders)

        shareholder_changes = []
        for shareholder in top_shareholders:
            current_shares = shareholder['current_shares']
            previous_shares = shareholder['previous_shares']
            shares_change = shareholder['shares_change']

            if previous_shares != 0:
                change_rate = shares_change / previous_shares
            else:
                change_rate = 0

            shareholder_changes.append((shares_change, change_rate))

        num_groups = len(shareholder_changes) // group_size
        result = {}

        for i in range(num_groups):
            start_index = i * group_size
            end_index = (i + 1) * group_size

            group_changes = [change for change, _ in shareholder_changes[start_index:end_index]]
            group_change_rates = [rate for _, rate in shareholder_changes[start_index:end_index]]

            avg_change = sum(group_changes) / group_size
            avg_change_rate = sum(group_change_rates) / group_size

            result[f'top_{(i+1)*10}_pct'] = {
                'avg_shares_change': avg_change,
                'avg_change_rate': avg_change_rate
            }

        return result
    
if __name__ == '__main__':
    analyzer = ShareholderAnalysis('AAPL')
    result = analyzer.analyze_top_shareholders(num_shareholders=100, group_size=10)
    print(result)
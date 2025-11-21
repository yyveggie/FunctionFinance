# 资讯数据
# 电报
# 接口：stock_telegraph_cls

# 目标地址：https://www.cls.cn/telegraph

# 描述：财联社-电报

# 限量：单次返回指定 symbol 的财联社-电报的数据

# 输入参数

# 名称	类型	描述
# symbol	str	symbol="全部"；choice of {"全部", "重点"}
# 输出参数

# 名称	类型	描述
# 标题	object	-
# 内容	object	-
# 发布日期	object	-
# 发布时间	object	-
# 接口示例：

import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从财联社下载实时新闻
'''
from data_connection.mongodb import MongoConnection
from proxy_pool.usable_ip import Usable_IP
import akshare as ak

class CLS_Real_Time_News(Usable_IP):
    def __init__(self, option, args={}):
        super().__init__(args)
        self.option = option
        self.db_connection = MongoConnection('Real_Time_News')
        self.source = "cls.cn"

    def download(self):
        stock_info_global_cls_df = ak.stock_info_global_cls(symbol=self.option)
        data_list = stock_info_global_cls_df.to_dict(orient='records')
        # self.db_connection.save_data('cls', self.source, data_list)
        return data_list

if __name__ == "__main__":
    option = '重点'  # ‘全部’，‘重点’
    c = CLS_Real_Time_News(option)
    print(c.download())
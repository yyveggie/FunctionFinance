# 互动平台
# 互动易-提问
# 接口: stock_irm_cninfo

# 目标地址: https://irm.cninfo.com.cn/

# 描述: 互动易-提问

# 限量: 单次返回近期 10000 条提问数据

# 输入参数

# 名称	类型	描述
# symbol	str	symbol="002594";
# 输出参数

# 名称	类型	描述
# 股票代码	object	-
# 公司简称	object	-
# 行业	object	-
# 行业代码	object	-
# 问题	object	-
# 提问者	object	-
# 来源	object	-
# 提问时间	datetime64[ns]	-
# 更新时间	datetime64[ns]	-
# 提问者编号	object	-
# 问题编号	object	-
# 回答ID	object	-
# 回答内容	object	-
# 回答者	object	-
# 接口示例

# import akshare as ak

# stock_irm_cninfo_df = ak.stock_irm_cninfo(symbol="002594")
# print(stock_irm_cninfo_df)
# 数据示例

#      股票代码 公司简称   行业  ...               回答ID           回答内容   回答者
# 0     002594  比亚迪  制造业  ...               None           None  None
# 1     002594  比亚迪  制造业  ...               None           None  None
# 2     002594  比亚迪  制造业  ...               None           None  None
# 3     002594  比亚迪  制造业  ...               None           None  None
# 4     002594  比亚迪  制造业  ...               None           None  None
#       ...  ...  ...  ...                ...            ...   ...
# 9995  002594  比亚迪  制造业  ...  58945327318695936  感谢您对公司的关心和支持！   比亚迪
# 9996  002594  比亚迪  制造业  ...  58945292958957568            谢谢！   比亚迪
# 9997  002594  比亚迪  制造业  ...  58945275779088384            谢谢！   比亚迪
# 9998  002594  比亚迪  制造业  ...  58945224239480832            谢谢！   比亚迪
# 9999  002594  比亚迪  制造业  ...  58945189879742464            谢谢！   比亚迪
# [10000 rows x 14 columns]
# 互动易-回答
# 接口: stock_irm_ans_cninfo

# 目标地址: https://irm.cninfo.com.cn/

# 描述: 互动易-回答

# 限量: 单次返回指定 symbol 的回答数据

# 输入参数

# 名称	类型	描述
# symbol	str	symbol="1495108801386602496"; 通过 ak.stock_irm_cninfo 来获取具体的提问者编号
# 输出参数

# 名称	类型	描述
# 股票代码	object	-
# 公司简称	object	-
# 问题	object	-
# 回答内容	object	-
# 提问者	object	-
# 提问时间	datetime64[ns]	-
# 回答时间	datetime64[ns]	-
# 接口示例

# import akshare as ak

# stock_irm_ans_cninfo_df = ak.stock_irm_ans_cninfo(symbol="1495108801386602496")
# print(stock_irm_ans_cninfo_df)
# 数据示例

#      股票代码 公司简称  ...                提问时间                回答时间
# 0  002594  比亚迪  ... 2023-07-08 04:12:53 2023-07-12 00:34:31
# [1 rows x 7 columns]
# 上证e互动
# 接口: stock_sns_sseinfo

# 目标地址: https://sns.sseinfo.com/company.do?uid=65

# 描述: 上证e互动-提问与回答

# 限量: 单次返回指定 symbol 的提问与回答数据

# 输入参数

# 名称	类型	描述
# symbol	str	symbol="603119"; 股票代码
# 输出参数

# 名称	类型	描述
# 股票代码	object	-
# 公司简称	object	-
# 问题	object	-
# 回答	object	-
# 问题时间	object	-
# 回答时间	object	-
# 问题来源	object	-
# 回答来源	object	-
# 用户名	object	-
# 接口示例

# import akshare as ak

# stock_sns_sseinfo_df = ak.stock_sns_sseinfo(symbol="603119")
# print(stock_sns_sseinfo_df)
# 数据示例

#       股票代码  公司简称  ... 回答来源              用户名
# 0   603119  浙江荣泰  ...   网站  guest_rNuyIaR0j
# 1   603119  浙江荣泰  ...   网站  guest_Dn88vsRvS
# 2   603119  浙江荣泰  ...   网站          g m g m
# 3   603119  浙江荣泰  ...   网站          g m g m
# 4   603119  浙江荣泰  ...   网站          g m g m
# 5   603119  浙江荣泰  ...   网站              柯旭西
# 6   603119  浙江荣泰  ...   网站          g m g m
# 7   603119  浙江荣泰  ...   网站             wujw
# 8   603119  浙江荣泰  ...   网站             wujw
# 9   603119  浙江荣泰  ...   网站             wujw
# 10  603119  浙江荣泰  ...   网站             wujw
# 11  603119  浙江荣泰  ...   网站             wujw
# 12  603119  浙江荣泰  ...   网站             wujw
# 13  603119  浙江荣泰  ...   网站             wujw
# 14  603119  浙江荣泰  ...   网站          g m g m
# 15  603119  浙江荣泰  ...   网站          g m g m
# 16  603119  浙江荣泰  ...   网站  guest_JmVsmnwYU
# 17  603119  浙江荣泰  ...   网站             ikun
# 18  603119  浙江荣泰  ...   网站              黄以牛
# 19  603119  浙江荣泰  ...   网站          g m g m
# 20  603119  浙江荣泰  ...   网站          g m g m
# 21  603119  浙江荣泰  ...   网站          g m g m
# 22  603119  浙江荣泰  ...   网站          g m g m
# 23  603119  浙江荣泰  ...   网站          g m g m
# 24  603119  浙江荣泰  ...   网站          g m g m
# 25  603119  浙江荣泰  ...   网站          g m g m
# 26  603119  浙江荣泰  ...   网站          g m g m
# 27  603119  浙江荣泰  ...   网站            赵子龙常山
# 28  603119  浙江荣泰  ...   网站          g m g m
# 29  603119  浙江荣泰  ...   网站          g m g m
# 30  603119  浙江荣泰  ...   网站          g m g m
# 31  603119  浙江荣泰  ...   网站          g m g m
# 32  603119  浙江荣泰  ...   网站             玩玩微博
# 33  603119  浙江荣泰  ...   网站       SummerIcey
# 34  603119  浙江荣泰  ...   网站            全深大最帅
# 35  603119  浙江荣泰  ...   网站  guest_ubuzXwHlL
# 36  603119  浙江荣泰  ...   网站            大股东1号
# 37  603119  浙江荣泰  ...   网站            江南奉化美
# 38  603119  浙江荣泰  ...   网站  guest_KhH5LPpO0
# 39  603119  浙江荣泰  ...   网站  guest_Dn88vsRvS
# 40  603119  浙江荣泰  ...   网站              龙投宝
# 41  603119  浙江荣泰  ...   网站       SummerIcey
# 42  603119  浙江荣泰  ...   网站  guest_Usy8rr8Ik
# 43  603119  浙江荣泰  ...   网站            赵子龙常山
# 44  603119  浙江荣泰  ...   网站            赵子龙常山
# [45 rows x 9 columns]
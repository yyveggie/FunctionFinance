import akshare as ak

# 若出现 KeyError: 'data'：雪球接口返回了错误 JSON（通常 error_code 400016），
# 内置 xq_a_token 已失效。先执行: pip install -U akshare
# 仍失败时：浏览器登录 xueqiu.com，从 Cookie 复制 xq_a_token，传入 token="..."
stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol="SH600000")
print(stock_individual_spot_xq_df)
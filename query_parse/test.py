import os
import logging
import json
from datetime import datetime, timedelta
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
from typing import List, Optional

openai_key = os.getenv('OpenAI_KEY')
client = instructor.patch(OpenAI(api_key=openai_key))

# 日志配置
def configure_logging():
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)

log_messages = []
def custom_print(message):
    if isinstance(message, dict) or isinstance(message, list): formatted_message = json.dumps(message, indent=4, ensure_ascii=False)
    else: formatted_message = str(message)
    log_messages.append(formatted_message)
    print(formatted_message)

# 日期相关函数
def get_current_date(): return [datetime.now().strftime("%Y-%m-%d")]
current_date = get_current_date()
def get_current_year(): return [str(datetime.now().year)]
current_year = get_current_year()
def get_date_days_ago(days):
    today = datetime.now()
    past_date = today - timedelta(days=days)
    return [past_date.strftime("%Y-%m-%d")]

def convert_json_to_dropdown_options(file_path):
    try:
        with open(file_path, 'r') as file: data = json.load(file)
        dropdown_options = [{'label': key, 'value': value} for key, value in data.items()]
        return dropdown_options
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# UserDetail 类
class UserDetail(BaseModel):
    stock_information: Optional[List[str]] = Field(
        description="Extract or infer the mentioned companies name, listing_exchanges and tickers from the query.",
        default=[],
        examples=[["{
                   'Apple': {
                            'listing_exchange 1': ['Nasdaq'],
                            'ticker 1': ['AAPL']
                            },
                   'Alibaba': {
                            'listing_exchange 1': ['NYSE'],
                            'ticker 1': ['BABA'],
                            'listing_exchange 2': ['HKEX'],
                            'ticker 2': ['09988'],
                            }
                }"]]
        )
    start_date: Optional[List[str]] = Field(
        description="Extract relevant date from the query, which is the beginning date of a time period. It may be necessary to infer forward from the current date.", 
        default_factory=get_current_date,
        examples=[["2023-12-31", "2019-10-01"]]
        )
    end_date: Optional[List[str]] = Field(
        description="Extract the relevant date from the query, which is the end date of a time period.",
        default_factory=get_current_date,
        examples=[["2024-01-01", "2022-09-29"]]
        )
    specific_date: Optional[List[str]] = Field(
        description="Extract relevant date from query, which is a specific date.",
        default_factory=get_current_date,
        examples=[["2015-01-01", "2022-12-12"]]
        )
    year: Optional[List[str]] = Field(
        description="Extract the relevant year from the query, which is a specific year.",
        default_factory=get_current_year,
        examples=[["1995", "2022", "2024"]]
        )
    frequency: Optional[List[str]] = Field(
        description="Extract relevant frequency from the query, which is usually associated with the frequency of the report or data in finance. It can only select one from these three elements: 'annual', 'quarterly', 'trailing'",
        default=[],
        examples=[["annual", "quarterly", "trailing"]]
        )
    timeframe: Optional[List[str]] = Field(
        description="Extract the relevant time frames from the query, which usually describes the performance evaluation cycle of the investment, the analysis period of financial data, or the time range of market research. It can only select one from these seven elements: 'today', 'week', 'month', 'ytd', 'year', '3 years', '5 years'", 
        default=[],
        examples=[["today", "week", "month", "ytd", "year", "3 years", "5 years"]]
        )
    quarter: Optional[List[str]] = Field(
        description="Extract the relevant time range from the query, which is usually related to financial reporting, performance analysis, and forecasting and planning. It can only select one from these three elements: 'Q1', 'Q2', 'Q3', 'Q4'", 
        default=[],
        examples=[["Q1", "Q2", "Q3", "Q4"]]
        )
    country: Optional[List[str]] = Field(
        description="Extract the country from the query. If the country is not explicitly mentioned, it is usually inferred to be the country where the stock is listed on the exchange.",
        default=[],
        examples=[["US", "China", "Japan", "UK"]]
        )
    keyword: Optional[List[str]] = Field(
        description="Keyword is extracted from the query, generally related to finance, stocks and financial derivatives, and usually require searching in news web, ONLY ONE KEYWORD.",
        default=[],
        examples=[["Apple", "IPO", "Option", "Gold", "Futures"]]
        )
    keywords: Optional[List[str]] = Field(
        description="Keywords are extracted from the query, generally related to finance, stocks and financial derivatives, and usually require searching in news web, MORE THAN ONE KEYWORD.",
        default=[],
        examples=[["Apple", "IPO", "Option", "Gold", "Futures"]]
        )

# ----- Dash 应用和布局 -----
app = dash.Dash(__name__)

# 配置日志
configure_logging()

# 定义布局
app.layout = html.Div([
    # 创建下拉菜单（Spinner）
    dcc.Dropdown(
        id='spinner1',
        options=[
            {'label': 'category', 'value': 'category'},
            {'label': 'column', 'value': 'column'},
            {'label': 'plate', 'value': 'plate'},
            {'label': 'secid', 'value': 'secid'},
        ],
        placeholder="announcement_type_dict",
        value=None
    ),
    dcc.Dropdown(id='subspinner1'),  # 二级下拉菜单

    dcc.Dropdown(
        id='spinner2',
        options=convert_json_to_dropdown_options("ipos_upcoming_and_filings_categories.json"),
        placeholder="ipos_upcoming_and_filings_categories",
        value=None
    ),

    dcc.Dropdown(
        id='spinner3',
        options=convert_json_to_dropdown_options('stock_industries.json'),
        placeholder="stock_industries",
        value=None
    ),

    dcc.Dropdown(
        id='spinner4',
        options=convert_json_to_dropdown_options('stock_list.json'),
        placeholder="stock_lists",
        value=None
    ),

    dcc.Dropdown(
        id='spinner5',
        options=convert_json_to_dropdown_options('stock_ranking_categories.json'),
        placeholder="stock_ranking_categories",
        value=None
    ),

    dcc.Dropdown(
        id='spinner6',
        options=convert_json_to_dropdown_options('stock_sectors.json'),
        placeholder="stock_sectors",
        value=None
    ),

    # 创建文本输入框
    dcc.Input(id='query-input', type='text', placeholder='Do you have any question?'),
    # 创建提交按钮
    html.Button('确认选择', id='submit-button', n_clicks=0),
    # 创建一个用于显示结果的隐藏 div
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.Div(id='status-message', children=''),  # 新增的状态消息组件
    html.Button('点击显示日志', id='log-button', n_clicks=0),
    html.Pre(id='log-output', style={"white-space": "pre-wrap"}),  # 日志输出组件
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])
# 二级下拉菜单
sub_options = {
    'category': [{'label': '年报', 'value': 'category_ndbg_jjgg;'}, {'label': '半年报', 'value': 'category_bndbg_szsh;'}, {'label': '一季报', 'value': 'category_yjdbg_szsh;'}, {'label': '三季报', 'value': 'category_sjdbg_szsh;'}, {'label': '业绩预告', 'value': 'category_yjygjxz_szsh;'}, {'label': '权益分派', 'value': 'category_qyfpxzcs_szsh;'}, {'label': '董事会', 'value': 'category_dshgg_szsh;'}, {'label': '监事会', 'value': 'category_jshgg_szsh;'}, {'label': '股东大会', 'value': 'category_gddh_szsh;'}, {'label': '日常经营', 'value': 'category_rcjy_szsh;'}, {'label': '公司治理', 'value': 'category_gszl_szsh;'}, {'label': '中介报告', 'value': 'category_zj_szsh;'}, {'label': '首发', 'value': 'category_sf_szsh;'}, {'label': '增发', 'value': 'category_zf_szsh;'}, {'label': '股权激励', 'value': 'category_gqjl_szsh;'}, {'label': '配股', 'value': 'category_pg_szsh;'}, {'label': '解禁', 'value': 'category_jj_szsh;'}, {'label': '公司债', 'value': 'category_gszq_szsh;'}, {'label': '可转债', 'value': 'category_kzzq_szsh;'}, {'label': '其他融资', 'value': 'category_qtrz_szsh;'}, {'label': '股权变动', 'value': 'category_gqbd_szsh;'}, {'label': '补充更正', 'value': 'category_bcgz_szsh;'}, {'label': '澄清致歉', 'value': 'category_cqdq_szsh;'}, 
                 {'label': '风险提示', 'value': 'category_fxts_szsh;'}, {'label': '特别处理和退市', 'value': 'category_tbclts_szsh;'}, {'label': '退市整理期', 'value': 'category_tszlq_szsh;'}, {'label': '临时公告', 'value': 'category_lsgg;'}, {'label': '定期公告', 'value': 'category_dqgg;'}, {'label': '中介机构公告', 'value': 'category_zjjg;'}, {'label': '持续信息披露', 'value': 'category_cxpl;'}, {'label': '首次信息披露', 'value': 'category_scpl;'}, {'label': '招募设立', 'value': 'category_jjzm_jjgg;'}, {'label': '说明书更新', 'value': 'category_smsgx_jjgg;'}, {'label': '中报', 'value': 'category_bndbg_jjgg;'}, {'label': '季报', 'value': 'category_jdbg_jjgg;'}, {'label': '净值', 'value': 'category_jzgg_jjgg;'}, {'label': '投资组合', 'value': 'category_zhtz_jjgg;'}, {'label': '申购赎回', 'value': 'category_sgsh_jjgg;'}, {'label': '基金费率', 'value': 'category_jjfl_jjgg;'}, {'label': '销售渠道', 'value': 'category_xsqd_jjgg;'}, {'label': '分红', 'value': 'category_fh_jjgg;'}, {'label': '高管及基金经理', 'value': 'category_ggjjjl_jjgg;'}, {'label': '持有人大会', 'value': 'category_fecyr_jjgg;'}, {'label': '基本信息变更', 'value': 'category_jbxxbg_jjgg;'}, {'label': '其他', 'value': 'category_jgjg_qt;'}, {'label': '债券发行上市', 'value': 'category_zqfxss_zqgg;'}, 
                 {'label': '债券定期公告', 'value': 'category_zqdq_zqgg;'}, {'label': '债券付息公告', 'value': 'category_zqfx_zqgg;'}, {'label': '债券到期兑付停止交易公告', 'value': 'category_zqdqdftz_zqgg;'}, {'label': '债券其他公告', 'value': 'category_zqqt_zqgg;'}, {'label': '停复牌', 'value': 'category_jgjg_tfp;'}, {'label': '业务通知', 'value': 'category_jgjg_ywtz;'}, {'label': '批评处罚及公开谴责', 'value': 'category_jgjg_ppcfgkqz;'}, {'label': '交易风险提示', 'value': 'category_jgjg_jyfxts;'}, {'label': '保荐机构持续督导意见', 'value': 'category_bjjg;'}, {'label': '财务顾问持续督导意见', 'value': 'category_cwgw;'}],
    'column': [{'label': '深市', 'value': 'szse'}, {'label': '深主板', 'value': 'szseMain'}, {'label': '创业板', 'value': 'szseGem'}, {'label': '沪市', 'value': 'sse'}, {'label': '沪主板', 'value': 'sseMain'}, {'label': '科创板', 'value': 'sseKcp'}, {'label': '北交所', 'value': 'bj'}, {'label': '基金', 'value': 'fund'}, {'label': '债券', 'value': 'bond'}, {'label': '港股', 'value': 'hke'}, {'label': '三板', 'value': 'third'}, {'label': '调研', 'value': 'dy'}, {'label': '监管', 'value': 'regulator'}],
    'plate': [{'label': '深市', 'value': 'sz'}, {'label': '深主板', 'value': 'szmb'}, {'label': '创业板', 'value': 'szcy'}, {'label': '沪市', 'value': 'sh'}, {'label': '沪主板', 'value': 'shmb'}, {'label': '科创板', 'value': 'shkcp'}, {'label': '北交所', 'value': 'jgjg_bj'}, {'label': '港主板', 'value': 'hke'}, {'label': '港创业板', 'value': 'hkcy'}, {'label': '新三板', 'value': 'neeq'}, {'label': '老三板', 'value': 'staq'}, {'label': '深市债券', 'value': 'zqgg_szzq'}, {'label': '沪市债券', 'value': 'zqgg_shzq'}, {'label': '深交所', 'value': 'jgjg_sz'}, {'label': '上交所', 'value': 'jgjg_sh'}, {'label': '结算公司', 'value': 'jgjg_jsgs'}, {'label': '证监会', 'value': 'jgjg_zjh'}],
    'secid': [{'label': '安信基金', 'value': '9900022315'}, {'label': '百嘉基金', 'value': '9900052975'}, {'label': '宝盈基金', 'value': 'jjjl0000044'}, {'label': '北京京管泰富基金', 'value': '9900027035'}, {'label': '北信瑞丰基金', 'value': '9900028398'}, {'label': '贝莱德基金', 'value': '9900053074'}, {'label': '博道基金', 'value': '9900035745'}, {'label': '博时基金(国际)', 'value': 'QF000227'}, {'label': '博时基金', 'value': 'jjjl0000035'}, {'label': '博远基金', 'value': '9900039924'}, {'label': '渤海汇金证券资产', 'value': '9900035466'}, {'label': '财通基金', 'value': '9900021508'}, {'label': '财通证券资产', 'value': 'GD121415'}, {'label': '长安基金', 'value': '9900021482'}, {'label': '长城基金', 'value': 'jjjl0000045'}, {'label': '长江证券(上海)资产', 'value': 'GD121423'}, {'label': '长盛基金', 'value': 'jjjl0000038'}, {'label': '长信基金', 'value': 'jjjl0000069'}, {'label': '创金合信基金', 'value': '9900029154'}, {'label': '淳厚基金', 'value': '9900039373'}, {'label': '达诚基金', 'value': '9900042417'}, {'label': '大成基金', 'value': 'jjjl0000039'}, {'label': '德邦基金', 'value': '9900022507'}, {'label': '东方阿尔法基金', 'value': '9900035746'}, {'label': '东方汇理资产管理香港', 'value': 'QF000114'}, {'label': '东方基金', 'value': 'jjjl0000079'}, 
              {'label': '东海基金', 'value': '9900025646'}, {'label': '东吴基金', 'value': 'jjjl0000087'}, {'label': '东兴基金', 'value': '9900047095'}, {'label': '东兴证券', 'value': '9900008427'}, {'label': '东亚联丰投资', 'value': 'QF000028'}, {'label': '方正富邦基金', 'value': '9900021829'}, {'label': '蜂巢基金', 'value': '9900037100'}, {'label': '富安达基金', 'value': '9900019728'}, {'label': '富达基金管理(中国)', 'value': '9900053492'}, {'label': '富国基金', 'value': 'jjjl0000040'}, {'label': '富荣基金', 'value': '9900032713'}, {'label': '格林基金', 'value': '9900033930'}, {'label': '工银瑞信基金', 'value': 'jjjl0000090'}, {'label': '光大保德信基金', 'value': 'jjjl0000081'}, {'label': '广发基金', 'value': 'jjjl0000065'}, {'label': '国都证券', 'value': 'gfbj0870488'}, {'label': '国海富兰克林基金', 'value': 'jjjl0000084'}, {'label': '国金基金', 'value': '9900022147'}, {'label': '国开泰富基金', 'value': '9900027035'}, {'label': '国联安基金', 'value': 'jjjl0000051'}, {'label': '国联基金', 'value': '9900026588'}, {'label': '国融基金', 'value': '9900035734'}, {'label': '国寿安保基金', 'value': '9900027614'}, {'label': '国泰基金', 'value': 'jjjl0000034'}, {'label': '国投瑞银基金', 'value': 'jjjl0000046'}, {'label': '国新国证基金', 'value': '9900038878'}, 
              {'label': '嘉合基金', 'value': '9900029229'}, {'label': '嘉实基金', 'value': 'jjjl0000037'}, {'label': '建信基金', 'value': 'jjjl0000097'}, {'label': '江信基金', 'value': '9900025382'}, {'label': '交银施罗德基金', 'value': 'jjjl0000096'}, {'label': '金信基金', 'value': '9900031050'}, {'label': '金鹰基金', 'value': 'jjjl0000061'}, {'label': '金元顺安基金', 'value': '9900003461'}, {'label': '景顺长城基金', 'value': 'jjjl0000063'}, {'label': '九泰基金', 'value': '9900029088'}, {'label': '凯石基金', 'value': '9900035727'}, {'label': '路博迈基金管理(中国)', 'value': '9900053850'}, {'label': '民生加银基金', 'value': '9900005499'}, {'label': '明亚基金', 'value': '9900042416'}, {'label': '摩根基金(亚洲)', 'value': '9900031880'}, {'label': '摩根基金管理(中国)', 'value': 'jjjl0000080'}, {'label': '摩根士丹利基金管理(中国)', 'value': 'jjjl0000067'}, {'label': '南方基金', 'value': 'jjjl0000033'}, {'label': '南华基金', 'value': '9900033978'}, {'label': '农银汇理基金', 'value': '9900004441'}, {'label': '诺安基金', 'value': 'jjjl0000078'}, {'label': '诺德基金', 'value': '9900003002'}, {'label': '鹏华基金', 'value': 'jjjl0000036'}, {'label': '鹏扬基金', 'value': '9900033680'}, {'label': '平安基金', 'value': '9900017727'}, {'label': '浦银安盛基金', 'value': '9900004383'}, 
              {'label': '前海开源基金', 'value': '9900025283'}, {'label': '泉果基金', 'value': '9900054757'}, {'label': '融通基金', 'value': 'jjjl0000043'}, {'label': '瑞达基金', 'value': '9900051626'}, {'label': '山西证券', 'value': 'qsgn0000279'}, {'label': '上海东方证券资产', 'value': '9900022559'}, {'label': '上海国泰君安证券资产', 'value': 'GD065121'}, {'label': '上投摩根基金', 'value': 'jjjl0000080'}, {'label': '上银基金', 'value': '9900027118'}, {'label': '尚正基金', 'value': '9900053076'}, {'label': '申万菱信基金', 'value': 'jjjl0000074'}, {'label': '施罗德投资管理(香港)', 'value': '9900036215'}, {'label': '万家基金', 'value': 'jjjl0000050'}, {'label': '泓德基金', 'value': '9900030377'}, {'label': '睿远基金', 'value': '9900037923'}, {'label': '西部利得基金', 'value': '9900016888'}, {'label': '西藏东财基金', 'value': '9900042415'}, {'label': '先锋基金', 'value': '9900033259'}, {'label': '湘财基金', 'value': '9900037458'}, {'label': '新华基金', 'value': 'jjjl0000086'}, {'label': '新疆前海联合基金', 'value': '9900031678'}, {'label': '新沃基金', 'value': '9900031314'}, {'label': '鑫元基金', 'value': '9900027067'}, {'label': '信达澳亚基金', 'value': '9900000041'}, {'label': '信达澳银基金', 'value': '9900000041'}, {'label': '兴合基金', 'value': '9900053496'}, 
              {'label': '兴华基金', 'value': '9900047346'}, {'label': '兴业基金', 'value': '9900026037'}, {'label': '兴银基金', 'value': '9900027625'}, {'label': '兴证全球基金', 'value': 'jjjl0000077'}, {'label': '行健资产', 'value': '9900032049'}, {'label': '易方达基金', 'value': 'jjjl0000041'}, {'label': '易米基金', 'value': '9900053075'}, {'label': '益民基金', 'value': 'jjjl0000092'}, {'label': '银河基金', 'value': 'jjjl0000049'}, {'label': '银华基金', 'value': 'jjjl0000042'}, {'label': '英大基金', 'value': '9900025897'}, {'label': '永赢基金', 'value': '9900027308'}, {'label': '圆信永丰基金', 'value': '9900027958'}, {'label': '招商基金', 'value': 'jjjl0000060'}, {'label': '浙江浙商证券资产', 'value': 'GD081202'}, {'label': '浙商基金', 'value': '9900015857'}, {'label': '中庚基金', 'value': '9900037457'}, {'label': '中国人保资产', 'value': 'GD028463'}, {'label': '中海基金', 'value': 'jjjl0000083'}, {'label': '中航基金', 'value': '9900033023'}, {'label': '中加基金', 'value': '9900025898'}, {'label': '中金基金', 'value': '9900028118'}, {'label': '中科沃土基金', 'value': '9900031644'}, {'label': '中欧基金', 'value': 'jjjl0000101'}, {'label': '中泰证券(上海)资产', 'value': '9900037883'}, {'label': '中信保诚基金', 'value': 'jjjl0000099'}, {'label': '中信建投基金', 'value': '9900027036'}, 
              {'label': '中银国际证券', 'value': 'qsgn0000638'}, {'label': '中银基金', 'value': 'jjjl0000072'}, {'label': '中邮创业基金', 'value': 'jjjl0000100'}, {'label': '朱雀基金', 'value': '9900038644'}]
    }

# ----- 回调定义 -----
custom_print("程序运行中...")
# 定义二级下拉菜单的回调
@app.callback(Output('subspinner1', 'options'), Input('spinner1', 'value'))
def set_subspinner1_options(selected_value):
    if not selected_value or selected_value not in sub_options:
        return []  # 如果未选择或选择无效，则返回空列表
    return sub_options.get(selected_value, [])  # 获取对应的二级选项列表

# 主回调函数
@app.callback(
    Output('intermediate-value', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('spinner1', 'value'), State('subspinner1', 'value'),
     State('spinner2', 'value'),
     State('spinner3', 'value'),
     State('spinner4', 'value'), 
     State('spinner5', 'value'), 
     State('spinner6', 'value'),
     State('query-input', 'value')]
)
def update_output(n_clicks, value1, subvalue1, value2, value3, value4, value5, value6, query):
    if n_clicks > 0:
        logging.info(f"选择1: {value1}, 子选择1: {subvalue1}, 选择2: {value2}, 选择3: {value3}, 选择4: {value4}, 选择5: {value5}, 选择6: {value6}, 查询: {query}")
        custom_print("Query 解析中...")
        result = process_query(query, value1, subvalue1, value2, value3, value4, value5, value6)
        return json.dumps(result)
    return json.dumps({})  # 如果没有点击，则返回空的字典

# 日志显示回调
@app.callback(
    Output('log-output', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_logs(n):
    if n % 10 == 0:  # 例如，每10次间隔更新一次日志
        return html.Div([html.Div(log) for log in log_messages])
    return dash.no_update  # 其他情况不更新页面

def process_query(query, value1, subvalue1, value2, value3, value4, value5, value6):
    user: UserDetail = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=UserDetail,
        messages=[
            {"role": "system", "content": "You are now a world-renowned financial expert. You are familiar with the information of listed companies on various exchanges. You need to extract entities based on user query, or infer information to fill in the values of the following variables. Note that some variables have annotates, and you need to follow the rules of annotates. I'll give you some examples below. You should response in English. Speaking of date, I can tell you that today's date is " + current_date[0]},
            {"role": "system", "content": 
            f'''
            examples: 
            1. query:
                    'What is Apple's share price today?'
                response:
                    stock_information: [
                            'Apple': 
                            {
                            'listing_exchange 1': ['Nasdaq'],
                            'ticker 1': ['AAPL'],
                    }],
                    start_date: {current_date},
                    end_date: {current_date},
                    specific_date: {current_date},
                    year: {current_year},
                    frequency: None,
                    timeframe: 'today',
                    quarter: None,
                    country: ['us'],
                    keyword: ['Apple'],
                    keywords: ['Apple', 'share price']
            2. query:
                    'What's the latest news about Alibaba?'
                response:
                    stock_information: [
                            'Alibaba': 
                            {
                            'listing_exchange 1': ['NYSE'],
                            'ticker 1': ['BABA'],
                            'listing_exchange 2': ['HKEX'],
                            'ticker 1': ['09988'],
                            }
                    ]
                    start_date: {current_date},
                    end_date: {current_date},
                    specific_date: {current_date},
                    year: {current_year},
                    frequency: None,
                    timeframe: 'today',
                    quarter: None,
                    country: ['us'],
                    keyword: ['Alibaba'],
                    keywords: ['Alibaba', 'news']
            3. query:
                    'For the gaming market, within the past month(past 30 days), who performs better, NVIDIA or Tencent?'
                response:
                    stock_information: [
                            'NVIDIA': 
                            {
                            'listing_exchange 1': ['Nasdaq'],
                            'ticker 1': ['NVDA'],
                            },
                            'TECENT': 
                            {
                            'listing_exchange 1': ['HKEX'],
                            'ticker 1': ['0700'],
                            },
                    ]
                    start_date: {get_date_days_ago(30)},    # becase past 30 days
                    end_date: {current_date},
                    specific_date: None,
                    year: {current_year},
                    frequency: None,
                    timeframe: None,
                    quarter: None,
                    country: ['us', 'china'],
                    keyword: ['NVIDIA'] or ['Tencent'],
                    keywords: ['NVIDIA', 'Tencent']   
            '''
            },
            {"role": "user", "content": query}
        ]
    ) # type: ignore

    data = {
        "stock_information": user.stock_information,
        "start_date": user.start_date,
        "end_date": user.end_date,
        "specific_date": user.specific_date,
        "year": user.year,
        "frequency": user.frequency,
        "timeframe": user.timeframe,
        "quarter": user.quarter,
        "country": user.country,
        "keyword": user.keyword,
        "keywords": user.keywords,
        "spinner1_value": value1,
        "subspinner1_value": subvalue1,
        "spinner2_value": value2,
        "spinner3_value": value3,
        "spinner4_value": value4,
        "spinner5_value": value5,
        "spinner6_value": value6,
    }
    custom_print("解析如下:\n")
    custom_print(data)
    with open('temp_config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
    
    return data

if __name__ == '__main__':
    app.run_server(debug=True)
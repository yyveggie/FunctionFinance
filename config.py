import ast
import json
from datetime import datetime, timedelta
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.chains import LLMChain
from datetime import datetime, timedelta
import os
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_CONFIG_DIR)
TEMP_CONFIG_JSON = os.path.join(_CONFIG_DIR, 'temp_config.json')


class Parser:
    def __init__(self, llm, query):
        self.parser_llm = llm
        self.llm = llm
        self.query = query
        self.current_date = [datetime.now().strftime("%Y-%m-%d")]
        self.current_year = [str(datetime.now().year)]

    def __call__(self):
        return self.parse()

    def get_date_days_offset(self, given_date, days):
        date_obj = datetime.strptime(given_date, "%Y-%m-%d")
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime("%Y-%m-%d")

    def parse(self):
        examples = [
            {"query": "What is Apple's share price today?",
                "information": f"'company_en': [['Apple']], 'company_cn': [['苹果']], 'listing_exchange': [['NASDAQ']], 'ticker': [['AAPL']], 'cryptocurrency': None, 'start_date': {self.current_date}, 'end_date': {self.current_date}, 'specific_date': {self.current_date}, 'year': {self.current_year}, 'frequency': None, 'timeframe': ['today'], 'quarter': None, 'country': [['us']], 'keyword_cn': ['苹果', '股价'], 'keyword_en': ['Apple', 'share price']"},
            {"query": "What's the latest news about Alibaba?",
                "information": f"'company_en': [['Alibaba']], 'company_cn': [['阿里巴巴']], 'listing_exchange': [['NYSE'], ['HKEX']], 'ticker': [['BABA'], ['9988']], 'cryptocurrency': None, 'start_date': {self.current_date}, 'end_date': {self.current_date}, 'specific_date': {self.current_date}, 'year': {self.current_year}, 'frequency': None, 'timeframe': ['today'], 'quarter': None, 'country': [['us']], 'keyword_cn': ['阿里巴巴', '新闻'],'keyword_en': ['Alibaba', 'news']"},
            {"query": "For the past 30 days in gaming market, who performs better, NVIDIA or Tencent?",
                "information": f"'company_en': [['NVIDIA'], ['TECENT']], 'company_cn': [['英伟达'], ['腾讯']], 'listing_exchange': [['NASDAQ'], ['HKEX']], 'ticker': [['NVDA'], ['0700']], 'cryptocurrency': None, 'start_date': {self.get_date_days_offset(self.current_date[0], -30)}, 'end_date': {self.current_date}, 'specific_date': None, 'year': {self.current_year}, 'frequency': None, 'timeframe': None, 'quarter': None, 'country': [['us'], ['china']], 'keyword_cn': ['英伟达', '腾讯'], 'keyword_en': ['NVIDIA', 'Tencent']"},
            {"query": "How did PepsiCo's P/E ratio perform in the first quarter of 2023?",
                "information": f"'company_en': [['PepsiCo']], 'company_cn': [['百事']], 'listing_exchange': [['NASDAQ']], 'ticker': [['PEP']], 'cryptocurrency': None, 'start_date': ['2023-01-01'], 'end_date': ['2023-03-31'], 'specific_date': None, 'year': ['2023'], 'frequency': ['quarterly'], 'timeframe': None, 'quarter': ['Q1'], 'country': [['us']], 'keyword_cn': ['百事', '市盈率'], 'keyword_en': ['PepsiCo', 'P/E ratio']"},
            {"query": "Give me BYD and Tesla's EPS for the 3 years before 2024, and then make a forecast for the future EPS.",
                "information": f"'company_en': [['BYD'], ['Tesla']], 'company_cn': [['比亚迪'], ['特斯拉']], 'listing_exchange': [['HKEX', 'SZSE'], ['NASDAQ']], 'ticker': [['1211', '002594'], ['TSLA']], 'cryptocurrency': None, 'start_date': {self.get_date_days_offset('2024-01-01', -365*3)}, 'end_date': ['2024-01-01'], 'specific_date': None, 'year': ['2023'], 'frequency': None, 'timeframe': ['3 years'], 'quarter': None, 'country': [['china'], ['us']], 'keyword_cn': ['比亚迪', '特斯拉', '每股利润'],'keyword_en': ['BYD', 'Tesla', 'EPS']"},
        ]
        example_formatter_template = """
            Query: {query}
            Information: {information}
        """
        example_prompt = PromptTemplate(
            input_variables=["query", "information"],
            template=example_formatter_template,
        )
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            suffix="QUERY: {input}\n Information:",
            input_variables=["input"],
            example_separator="\n\n",
            prefix='''
            You are now a well-known financial industry expert around the world. You are familiar with the information of listed companies on various exchanges. Your task is to extract or infer the values of the following variables from the query: Note that the presence of a list means that the variable can only select one element from the list. Here are the required variables:
            'company_en': English name(s) of the company/companies.
            'company_cn': Chinese name(s) of the company/companies.
            'listing_exchange': The stock exchange(s) where company/companies is/are listed.
            'ticker': Stock ticker(s) of the stock exchange(s) on which the company/companies is/are listed.
            'cryptocurrency': Mentioned cryptocurrencies.
            'start_date': The beginning date of a time period.
            'end_date': The end date of a time period.
            'specific_date': The specific date to search.
            'year': The specific year to search.
            'keyword_cn': Chinese Keyword(s) is/are extracted from the query.
            'keyword_en': English Keyword(s) is/are extracted from the query.
            'frequency': MUST one of these three elements: ['annual', 'quarterly', 'trailing']. Associated with the frequency of the report or data in finance.
            'timeframe': MUST one of these seven elements: ['today', 'week', 'month', 'ytd', 'year', '3 years', '5 years']. Describes the performance evaluation cycle of the investment, or the analysis period of financial data.
            'quarter': MUST one of these four elements: ['Q1', 'Q2', 'Q3', 'Q4']. Related to financial reporting, performance analysis, and forecasting and planning.
            'country': The country/countries where the company/companies is/are listed.
            '''
        )

        chain = LLMChain(llm=self.llm, prompt=few_shot_prompt)

        response = chain.invoke(self.query)
        content_str = "{" + response["text"] + "}".replace('\n', ', ')
        content_dict = ast.literal_eval(content_str)

        data = {
            "company_en": content_dict["company_en"],
            "company_cn": content_dict["company_cn"],
            "listing_exchange": content_dict["listing_exchange"],
            "ticker": content_dict["ticker"],
            "cryptocurrency": content_dict["cryptocurrency"],
            "start_date": content_dict["start_date"],
            "end_date": content_dict["end_date"],
            "specific_date": content_dict["specific_date"],
            "year": content_dict["year"],
            "frequency": content_dict["frequency"],
            "timeframe": content_dict["timeframe"],
            "quarter": content_dict["quarter"],
            "country": content_dict["country"],
            "keyword_cn": content_dict["keyword_cn"],
            "keyword_en": content_dict["keyword_en"],
        }

        with open(TEMP_CONFIG_JSON, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

        res = core.run(self.llm, self.query)
        return res


def sele_config(op, iphone=True, headless=False):
    op.add_experimental_option("detach", True)
    op.add_argument('--disable-gpu')
    op.add_argument('--disable-blink-features=AutomationControlled')
    op.add_experimental_option('excludeSwitches', ['enable-automation'])
    # Turn-off userAutomationExtension
    op.add_experimental_option("useAutomationExtension", False)
    op.add_argument('--no-sandbox')
    op.add_argument('--start-maximized')
    op.add_argument('--start-fullscreen')
    op.add_argument('--single-process')
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument("--incognito")
    op.add_argument("disable-infobars")
    op.add_argument('blink-settings=imagesEnabled=false')
    prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    op.add_experimental_option('prefs', prefs)
    if headless:
        op.add_argument('--headless')
    if iphone:
        op.add_argument(
            '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')
    return op


def read_screen_dict(keys, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    values = [data.get(key) for key in [keys]]
    return values


def read_index_dict(out_key, key, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        value = data[out_key][key[0]]
    except:
        value = None
    return value


def ensure_nested_list(lst):
    return [item if isinstance(item, list) else [item] for item in lst]


def read_list(lst):
    with open("./category_files/stock_list_url.json", "r", encoding="utf-8") as f:
        return json.load(f)[lst]


def get_current_date(): return [datetime.now().strftime('%Y-%m-%d')]


current_date = get_current_date()
def get_current_year(): return [str(datetime.now().year)]


current_year = get_current_year()


def get_date_days_offset(given_date, days):
    date_obj = datetime.strptime(given_date, '%Y-%m-%d')
    new_date = date_obj + timedelta(days=days)
    return new_date.strftime('%Y-%m-%d')


if os.path.isfile(TEMP_CONFIG_JSON):
    with open(TEMP_CONFIG_JSON, 'r', encoding='utf-8') as file:
        temp_config = json.load(file)
else:
    temp_config = {}

try:
    country = ensure_nested_list(temp_config.get('country'))
except:
    country = [['us'], ['china']]
if country == [''] or country == None or country == [None] or country == [[None]]:
    country = [['us'], ['china']]
try:
    company_en = ensure_nested_list(temp_config.get('company_en'))
except:
    company_en = None
try:
    company_cn = ensure_nested_list(temp_config.get('company_cn'))
except:
    company_cn = None
try:
    listing_exchange = ensure_nested_list(temp_config.get('listing_exchange'))
except:
    listing_exchange = None
try:
    keyword_cn = temp_config.get('keyword_cn')
except:
    keyword_cn = None
try:
    keyword_en = temp_config.get('keyword_en')
except:
    keyword_en = None
try:
    ticker = ensure_nested_list(temp_config.get('ticker'))
except:
    ticker = None
try:
    ticker_listing_exchange = [[f'{a[0]}:{b[0]}'] for a, b in zip(ensure_nested_list(
        temp_config.get('ticker')), ensure_nested_list(temp_config.get('listing_exchange')))]
except:
    ticker_listing_exchange = None
try:
    start_date = temp_config.get('start_date')
except:
    start_date = current_date
if start_date == [''] or start_date == None or start_date == [None] or start_date == [[None]]:
    start_date = current_date
try:
    end_date = temp_config.get('end_date')
except:
    end_date = current_date
if end_date == [''] or end_date == None or end_date == [None] or end_date == [[None]]:
    end_date = current_date
try:
    specific_date = temp_config.get('specific_date')
except:
    specific_date = current_date
if specific_date == [''] or specific_date == None or specific_date == [None] or specific_date == [[None]]:
    specific_date = current_date
try:
    year = temp_config.get('year')
except:
    year = current_year
if year == [''] or year == None or year == [None] or year == [[None]]:
    year = current_year
try:
    frequency = temp_config.get('frequency')  # annual, quarterly, trailing
except:
    frequency = ['annual']
if frequency == [''] or frequency == None or frequency == [None] or frequency == [[None]]:
    frequency = ['annual']
try:
    # today, week, month, ytd, year, 3 years, 5 years
    timeframe = temp_config.get('timeframe')
except:
    timeframe = ['ytd']
if timeframe == [''] or timeframe == None or timeframe == [None] or timeframe == [[None]]:
    timeframe = ['ytd']
try:
    quarter = temp_config.get('quarter')
except:
    quarter = ['Q1']
if quarter == [''] or quarter == None or quarter == [None] or quarter == [[None]]:
    quarter = ['Q1']
try:
    public_announcement_type = temp_config.get('public_announcement_type')
except:
    public_announcement_type = ['A股']
if public_announcement_type == [''] or public_announcement_type == None or public_announcement_type == [None] or public_announcement_type == [[None]]:
    public_announcement_type = ['A股']
try:
    announcement_type = read_index_dict('category', temp_config.get(
        'announcement_type'), './category_files/announcement_type.json')
except:
    announcement_type = read_index_dict(
        'category', ['年报'], './category_files/announcement_type.json')
if announcement_type == [''] or announcement_type == None or announcement_type == [None] or announcement_type == [[None]]:
    announcement_type = read_index_dict(
        'category', ['年报'], './category_files/announcement_type.json')
try:
    ranking_category = read_screen_dict(temp_config.get(
        'stock_ranking_category'), './category_files/stock_ranking_category.json')
except:
    ranking_category = read_screen_dict(
        'Industry', './category_files/stock_ranking_category.json')
if ranking_category == [''] or ranking_category == None or ranking_category == [None] or ranking_category == [[None]]:
    ranking_category = read_screen_dict(
        'Industry', './category_files/stock_ranking_category.json')
try:
    financial_category = read_screen_dict(temp_config.get(
        'financial_category'), './category_files/ipos_upcoming_and_filings_category.json')
except:
    financial_category = read_screen_dict(
        'Market Cap', './category_files/ipos_upcoming_and_filings_category.json')
if financial_category == [''] or financial_category == None or financial_category == [None] or financial_category == [[None]]:
    financial_category = read_screen_dict(
        'Market Cap', './category_files/ipos_upcoming_and_filings_category.json')
try:
    sector = read_screen_dict(temp_config.get(
        'sector'), './category_files/stock_sector.json')
except:
    sector = read_screen_dict(
        'Financials', './category_files/stock_sector.json')
if sector == [''] or sector == None or sector == [None] or sector == [[None]]:
    sector = read_screen_dict(
        'Financials', './category_files/stock_sector.json')
try:
    industry = read_screen_dict(temp_config.get(
        'industry'), './category_files/stock_industry.json')
except:
    industry = read_screen_dict(
        'Software - Infrastructure', './category_files/stock_industry.json')
if industry == [''] or industry == None or industry == [None] or industry == [[None]]:
    industry = read_screen_dict(
        'Software - Infrastructure', './category_files/stock_industry.json')
try:
    list_name = read_screen_dict(temp_config.get(
        'stock_list'), './category_files/stock_list.json')[0]
except:
    list_name = read_screen_dict(
        'Biggest Companies By Market Cap', './category_files/stock_list.json')[0]
if list_name == [''] or list_name == None or list_name == [None] or list_name == [[None]]:
    list_name = read_screen_dict(
        'Biggest Companies By Market Cap', './category_files/stock_list.json')[0]
try:
    stock_list = read_list(read_screen_dict(temp_config.get(
        'stock_list'), './category_files/stock_list.json')[0])
except:
    stock_list = read_list('Biggest Companies By Market Cap')
try:
    trade = temp_config.get('trade')
except:
    trade = ['金融业']
if trade == [''] or trade == None or trade == [None] or trade == [[None]]:
    trade = ['金融业']
try:
    fund_company = read_index_dict('secid', temp_config.get(
        'fund_company'), './category_files/announcement_type.json')
except:
    fund_company = None
try:
    column = [read_index_dict('column', temp_config.get(
        'column'), './category_files/announcement_type.json')]
except:
    column = [read_index_dict(
        'column', ['沪市'], './category_files/announcement_type.json')]
if column == [''] or column == None or column == [None] or column == [[None]]:
    column = [read_index_dict(
        'column', ['沪市'], './category_files/announcement_type.json')]
try:
    plate = [read_index_dict('plate', temp_config.get(
        'plate'), './category_files/announcement_type.json')]
except:
    plate = [read_index_dict(
        'plate', ['沪市'], './category_files/announcement_type.json')]
if plate == [''] or plate == None or plate == [None] or plate == [[None]]:
    plate = [read_index_dict(
        'plate', ['沪市'], './category_files/announcement_type.json')]
try:
    cryptocurrency = temp_config.get('cryptocurrency')
except:
    cryptocurrency = ['BTC']
if cryptocurrency == [''] or cryptocurrency == None or cryptocurrency == [None] or cryptocurrency == [[None]]:
    cryptocurrency = ['BTC']
try:
    subreddit = temp_config.get('subreddit')
except:
    subreddit = ['Stocks']
if subreddit == [''] or subreddit == None or subreddit == [None] or subreddit == [[None]]:
    subreddit = ['Stocks']
try:
    time_filter = temp_config.get('interval')
except:
    time_filter = ['day']
if time_filter == [''] or time_filter == None or time_filter == [None] or time_filter == [[None]]:
    time_filter = ['day']
try:
    listing = temp_config.get('listing')
except:
    listing = ['hot']
if listing == [''] or listing == None or listing == [None] or listing == [[None]]:
    listing = ['hot']

config = {
    'company_cn': company_cn,
    'listing_exchange': listing_exchange,
    'keyword_cn': keyword_cn,
    'keyword_en': keyword_en,
    'ticker': ticker,
    'ticker:listing_exchange': ticker_listing_exchange,
    'country': country,
    'start_date': start_date,
    'end_date': end_date,
    'specific_date': specific_date,

    'year': year,
    'frequency': frequency,
    'timeframe': timeframe,
    'quarter': quarter,

    'public_announcement_type': public_announcement_type,
    'announcement_type': announcement_type,
    'ranking_category': ranking_category,   # 可多选
    'financial_category': financial_category,   # 可多选
    'sector': sector,
    'industry': industry,
    'list_name': list_name,
    'stock_list': stock_list,
    'trade': trade,
    'fund_company': fund_company,
    'filing_type': '10-K',  # 10-K, 10-Q
    'column': column,
    'plate': plate,
    'cryptocurrency': cryptocurrency,
    'subreddit': subreddit,
    'time_filter': time_filter,
    'listing': listing,

    'sele_config': sele_config,
    'num_workers': 2,
    'sec_filings_amount': 2,
    'max_retry': 5,
    'proxy_pages': 5,
    'user': ['elonmusk', 'bbcchinese'],
}

# print(config['ranking_category'])

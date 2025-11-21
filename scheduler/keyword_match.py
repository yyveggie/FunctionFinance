import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import json
import spacy
import asyncio
import openai
import instructor
from nltk.corpus import wordnet
from data_connection.mongodb import AsyncMongoConnection
from config_loader import (
    GPT4O,
    BASE_URL,
    ZEN_API_KEY,
    OPENAI_API_KEY
)

client = instructor.from_openai(openai.AsyncOpenAI(
    # base_url=BASE_URL,
    api_key=OPENAI_API_KEY,  # type: ignore
    )
)

from pydantic import BaseModel, Field, field_validator

ALLOWED_DATA_TYPES = [
    "Market Overview Information", "Investor Sentiment and Behavior", "Block Trading and Capital Flows Data",
    "Goodwill Data", "Risk Management Data", 'Shareholder and Equity Information',
    'Analyst/Institutional Recommendations/Ratings/Reports', 'Forecast Data', 'Company/Stock Profile',
    'Investment Portfolio Statements', 'Company Announcements', 'Quote Data', 'Volume and Transaction Data',
    'Market Indices and Sentiment Data', 'Margin Trading and Short Selling Data',
    'Venture Capital and Funding Data', 'Insider Trading and Shareholding Patterns', 'Financial Ratios',
    'Initial Public Offerings Data', 'Foreign Exchange Rates', 'Income Statements', 'Economic Indicators',
    'Restricted Stock Information', 'Balance Sheets', 'Social Media and Network Analysis',
    'Technical Analysis Data', 'Cash Flow Statements', 'Corporate Filings', 'Merger and Acquisition Data', 'Stock Lists'
]
ALLOWED_DATE_TYPES = ['-', 'Now', 'Most Recent Trading Date', 'Recent Period', 'Date Range', 'Historical', 'Specific']
ALLOWED_FREQUENCIES = ['-', 'Real-Time', 'Intraday', 'Tick', 'Secondly', 'Minutely', 'Hourly', 'Daily',
                       'Weekly', 'Monthly', 'Quarterly', 'Annually', 'Reportly']
ALLOWED_SPECIFIC_OR_ALL = ["Specific", "Nonspecific"]
ALLOWED_LISTED_COUNTRIES = ['US', 'China', 'Hong Kong']


class QueryCompletionOutput(BaseModel):
    data_type: str = Field(..., description="Required type of financial data")
    date_type: str = Field(..., description="Time range needed for the data")
    specific_or_all: str = Field(..., description="Whether data is for single stock/company or nonspecific")
    listed_country_or_region: str = Field(..., description="Listed country or region")
    frequency: str = Field(..., description="Frequency of data recording")

    @field_validator('data_type')
    def validate_data_type(cls, value):
        data_types = [dt.strip() for dt in value.split(',')]
        invalid = [dt for dt in data_types if dt not in ALLOWED_DATA_TYPES]
        if invalid:
            raise ValueError(f"Invalid data_type value(s): {', '.join(invalid)}")
        if len(data_types) != 3:
            raise ValueError(f"data_type must have 3 values, got {len(data_types)}")
        return value

    @field_validator('specific_or_all')
    def validate_specific_or_all(cls, value):
        if value not in ALLOWED_SPECIFIC_OR_ALL:
            raise ValueError(f"Invalid specific_or_all value: {value}")
        return value

    @field_validator('listed_country_or_region')
    def validate_listed_country_or_region(cls, value):
        if value not in ALLOWED_LISTED_COUNTRIES:
            raise ValueError(f"Invalid listed_country_or_region value: {value}")
        return value

    @field_validator('date_type')
    def validate_date_type(cls, value):
        if value not in ALLOWED_DATE_TYPES:
            raise ValueError(f"Invalid date_type value: {value}")
        return value

    @field_validator('frequency')
    def validate_frequency(cls, value):
        frequencies = [fr.strip() for fr in value.split(',')]
        invalid = [fr for fr in frequencies if fr not in ALLOWED_FREQUENCIES]
        if invalid:
            raise ValueError(f"Invalid data_type value(s): {', '.join(invalid)}")
        return value
    

class ToolkitOutput(BaseModel):
    translation: str
    toolkit: str

    @field_validator('toolkit')
    def validate_toolkit(cls, toolkit):
        allowed_toolkits = ['Stock_Data', ...]  # 添加其他允许的工具包名称
        # more options to do: 'futures_data', 'bond_data', 'options_data', 'forex_data', 'currency_data', 'spot_data', 'interest_rate_data',
        # 'private_fund_data', 'mutual_fund_data', 'index_data', 'macroeconomic_data', 'cryptocurrency_data', 'banking_data',
        # 'volatility_data', 'multi_factor_data', 'migration_data', 'high_frequency_data'
        if toolkit not in allowed_toolkits:
            raise ValueError(f'Invalid toolkit: {toolkit}. Allowed values are: {allowed_toolkits}')
        return toolkit
    

class KeywordMatch:
    def __init__(self, query) -> None:
        self.query = query
        self.nlp = spacy.load("en_core_web_sm")
        self.match_threshold = 1  # 设置匹配标准x
        self.rematch_threshold = 10  # 当匹配个数小于指定个数时，重新匹配
        self.example = json.dumps({"data_type": "Quote Data, Volume and Transaction Data, Financial Ratios", "date_type": "Now", "specific_or_all": "Nonspecific", "listed_country_or_region": "China", "frequency": "Real-Time"})

    async def __call__(self):
        reason_info = await self.query_complete(self.query)
        reason_dict = {
            "data_type": reason_info.data_type,
            "date_type": reason_info.date_type,
            "specific_or_all": reason_info.specific_or_all,
            "listed_country_or_region": reason_info.listed_country_or_region,
            "frequency": reason_info.frequency
        }
        type_, query_eng = await self.data_type_select(self.query)
        matching_items = await self.find_matching_documents(type_, query_eng, reason_dict)
        return matching_items, query_eng, type_

    async def query_complete(self, query):
        response = await client.chat.completions.create(
            model=GPT4O,
            response_model=QueryCompletionOutput,
            max_retries=3,
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are a request completion expert for financial data needs. User requests often lack necessary parameters considered common knowledge. Your task is to infer these parameters:
                     - 'data_type': the required type of financial data, from which you MUST select the most suitable 3 types(NOTE: 3) from the list provided:
                        ['Market Overview Information','Investor Sentiment and Behavior','Block Trading and Capital Flows Data','Goodwill Data',Risk Management Data',
		                'Shareholder and Equity Information','Analyst/Institutional Recommendations/Ratings/Reports','Forecast Data','Company/Stock Profile',
                        'Investment Portfolio Statements','Company Announcements','Quote Data','Volume and Transaction Data','Market Indices and Sentiment Data',
		                'Margin Trading and Short Selling Data','Venture Capital and Funding Data','Insider Trading and Shareholding Patterns','Financial Ratios',
                        'Initial Public Offerings Data','Foreign Exchange Rates','Income Statements','Economic Indicators','Restricted Stock Information','Balance Sheets',
                        'Social Media and Network Analysis','Technical Analysis Data','Cash Flow Statements','Corporate Filings','Merger and Acquisition Data','Stock Lists'],
                     - 'date_type': the time range needed for the data, select most suitable time range from ['-','Now','Most Recent Trading Date','Recent Period','Date Range','Historical','Specific'] or '-' if uncertain
                     - 'specific_or_all': Whether data is for single stock/company ('Specific') or nonspecific ('Nonspecific')
                     - 'listed_country_or_region': Select from ['US','China','Hong Kong']
                     - 'frequency': The required frequency of data recording, for example, whether it is updated daily or every minute. you can select 1-3 options from the list provided. Only make a selection
                        when you are certain, otherwise, simply choose '-':
                        ['-','Real-Time','Intraday','Tick','Secondly','Minutely','Hourly','Daily','Weekly','Monthly','Quarterly','Annually','Reportly']
                    Output in JSON format with parameter names and selections only, e.g.: {self.example}
                    Note: JSON strings must use double quotes "", not single quotes ''.
                    """  
                },
                {
                    "role": "user",                
                    "content": query
                },
            ],
        )  # type: ignore
        return response

    async def data_type_select(self, query) -> str:
        response = await client.chat.completions.create(
            model=GPT4O,
            response_model=ToolkitOutput,
            max_retries=3,  # 在报错的情况下,会尝试一次重新把错误信息发送给 LLM,保证第二次输出正确
            messages=[
                {
                    "role": "system",
                    "content": f"""
                            You have two tasks:
                            1. Translate the given query into English word-for-word accurately, especially for entities like companies, stocks, organizations, etc.
                            2. Based on the translated query, select the toolkit that can solve the query's needs.
                                The toolkit names correspond to various types of financial data, and each toolkit contains tools related to that data type.
                                You need to infer the relevant financial data types from the query and output the toolkit name(s).
                                The available toolkits are: ['Stock_Data', ...]"
                    """  
                },
                {
                    "role": "user", 
                    "content": query
                },
            ],
        )  # type: ignore
        return response.toolkit, response.translation # type: ignore

    def lemmatize_text(self, text, include_synonyms=False):
        lemmatized_set = set()
        doc = self.nlp(text.lower())
        for token in doc:
            if token.is_punct:
                continue
            lemma = token.lemma_
            lemmatized_set.add(lemma)
            if include_synonyms:
                # 为每个词元查找近义词
                synonyms = self.find_synonyms(lemma)
                lemmatized_set.update(synonyms)
        return lemmatized_set

    def find_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            if syn is not None:
                for lem in syn.lemmas():
                    lemma_name = lem.name().replace('_', ' ')
                    synonyms.add(lemma_name)
        lemmatized_synonyms = self.lemmatize_text(
            ' '.join(synonyms), include_synonyms=False)
        return lemmatized_synonyms

    async def find_matching_documents(self, type, query_eng, agent_dict):
        self.mongo_conn = AsyncMongoConnection(db_name=type, host='localhost', port=27017)
        matching_items = []
        # 提取代理推理结果中的关键信息
        agent_countries = set(value.strip() for value in agent_dict['listed_country_or_region'].split(','))
        agent_data_types = set(value.strip() for value in agent_dict['data_type'].split(','))
        # 构建关键词集合
        query_keywords = set(query_eng.split() + agent_dict["date_type"].split() + agent_dict["frequency"].split() + agent_dict["listed_country_or_region"].split())
        # 对查询关键词进行词形还原并包括近义词
        lemmatized_query_keywords = self.lemmatize_text(" ".join(query_keywords), include_synonyms=True)
        # 获取数据库中的所有集合名称
        collection_names = await self.mongo_conn.db.list_collection_names()
        # 定义一个内部函数用于匹配文档
        async def match_documents(match_level):
            nonlocal matching_items
            matching_items.clear()  # 清空之前的匹配结果
            for collection_name in collection_names:
                collection = await self.mongo_conn.get_collection(collection_name)
                async for document in collection.find({}):
                    # 匹配 listed_country_or_region
                    item_countries = set([country.strip() for country in document.get("listed_country_or_region", "-").split(',')])
                    if not (item_countries & agent_countries) and "-" not in item_countries:
                        continue

                    # 如果匹配级别大于1,则检查数据类型是否匹配
                    if match_level > 1:
                        item_data_types = set([data_type.strip() for data_type in document.get("data_type", "-").split(',')])
                        if not (item_data_types & agent_data_types) and "-" not in item_data_types:
                            continue

                    # 如果匹配级别大于2,则进行关键词匹配
                    if match_level > 2:
                        match_keywords_flat = set()
                        # 在处理 additional_keywords 时也查找近义词
                        for keyword in document.get("additional_keywords", []):
                            lemmatized_keywords_with_synonyms = self.lemmatize_text(keyword, include_synonyms=True)
                            match_keywords_flat.update(lemmatized_keywords_with_synonyms)
                        if "description" in document:
                            description_keywords = self.lemmatize_text(" ".join([word for word in document["description"].split() if word.isalnum()]))
                            match_keywords_flat.update(description_keywords)
                        # 检查匹配项数量
                        if len(lemmatized_query_keywords & match_keywords_flat) < self.match_threshold:
                            continue
                    matching_items.append(document)

        # 首次匹配,考虑所有层级
        await match_documents(match_level=3)
        # 如果匹配项目少于10个,则重新匹配,忽略关键词匹配
        if len(matching_items) < self.rematch_threshold:
            await match_documents(match_level=2)
        # 如果匹配项目仍然少于10个,这次只进行第一层匹配
        if len(matching_items) < self.rematch_threshold:
            await match_documents(match_level=1)
        return matching_items

async def run(query):
    parser = KeywordMatch(query)
    return await parser()


async def main():
    queries = [
        "给我A股内幕行情数据",
    ]
    
    tasks = [asyncio.create_task(run(query)) for query in queries]
    results = await asyncio.gather(*tasks)
    
    for query, result in zip(queries, results):
        print(query)
        for item in result[0]:
            print(item["description"])

if __name__ == "__main__":
    asyncio.run(main())

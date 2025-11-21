import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import ast
import cohere
import asyncio
import instructor
from importlib import util
from openai import OpenAI, AsyncOpenAI
from actionweaver.llms import wrap
from textwrap import dedent
from scheduler import (
    keyword_match, 
    semantic_match,
    function_filter,
    function_reranker,
)
from config_loader import (
    GPT4O,
    OPENAI_API_KEY,
)

client = wrap(OpenAI(
    api_key=OPENAI_API_KEY,
))

client_classify = instructor.from_openai(AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    # base_url=BASE_URL,
))

class DataDownloadr:
    def __init__(self, search_keyword):
        self.search_keyword = search_keyword
        self.functions_calling_path = './apis/'

    async def __call__(self):
        return await self.function_calling(self.search_keyword)

    async def function_calling(self, query):
        match_list, query_eng, type_ = await keyword_match.run(query=query)
        filter_list = await function_filter.run(query=query_eng, functions_list=match_list)
        match_functions = await semantic_match.run(query=query, items=filter_list)
        functions = await self.collect_functions(function_names=match_functions, type=type_)
        rerank_functions = await function_reranker.run(query=query_eng, functions=functions)
        res = await self.calling(functions=rerank_functions, query=query_eng)
        return res

    async def calling(self, functions, query):
        messages = [
            {
                "role": "system",
                "content": dedent(
                    "Your task is to make function calls based on the user's query,"
                    "Don't ask the user for a parameter." 
                    "If you don't know which parameter value to choose, choose the one with the highest confidence, or use the default value."
            )
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        response = client.create(
            model=GPT4O,
            messages=messages,
            actions=functions,
        )
        return response.choices[0].message.content
    
    async def collect_functions(self, function_names, type):
        collected_functions = []
        search_directory = self.functions_calling_path + type
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_name = file_path.replace(
                        search_directory, '').replace('/', '.').strip('.py')
                    spec = util.spec_from_file_location(
                        module_name, file_path)
                    module = util.module_from_spec(
                        spec)  # type: ignore
                    if spec != None and spec.loader != None:
                        spec.loader.exec_module(module)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    tree = ast.parse(file_content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name in function_names:
                            action_func = getattr(module, node.name)
                            if callable(action_func):
                                collected_functions.append(action_func)
        return collected_functions


async def run(query):
    parser = DataDownloadr(query)
    return await parser()

if __name__ == '__main__':
            # "告诉我最新的涨停股池"
            # '请告诉我最新的英伟达股价和市盈率、市净率, 以及平安银行的股东信息',
            # "茅台2022年的利润表数据",
            # "帮我查看谷歌最新的股价和推荐师关于谷歌的推荐指数",
            # "美股中金融类的股票实时行情数据有吗？"
            # "有关于A股的股债利差数据吗？"
            # "查一下浙商银行最新股价"
            # '查一下茅台的利润表'
            # 'Get return data for all analysts in China from 2023-01-01 to 2023-12-31',
            # '茅台十大流通股东信息',
            # '帮我查看一下最新的谷歌报价数据', 
            # '浙商银行历史的市场行情',
        
    query = input('Hey! What do you want to ask? ')
    async def main():
        print(await run(query))

    asyncio.run(main())
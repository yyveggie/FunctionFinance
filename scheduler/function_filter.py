import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import instructor
from openai import AsyncOpenAI
from typing import List
from textwrap import dedent
from pydantic import BaseModel, field_validator
from config_loader import (
    ZEN_API_KEY,
    BASE_URL,
    GPT4O,
    GPT4
)

client = instructor.from_openai(AsyncOpenAI(
    api_key=ZEN_API_KEY,
    base_url=BASE_URL
))

class FunctionFiltering(BaseModel):
    indices: List[int]

    @field_validator('indices')
    def validate_indices(cls, indices):
        if not all(isinstance(i, int) for i in indices):
            raise ValueError('All indices must be integers.')
        return indices

class FilterFunctions:
    def __init__(self, query, functions: List[dict]):
        self.query = query
        self.functions = functions
        self.function_indices = {i: func for i, func in enumerate(functions, start=1)}
        self.reverse_indices = {str(func): i for i, func in self.function_indices.items()}

    async def __call__(self):
        return await self.filter(self.query)

    def _get_function_info(self, functions: list):
        function_info = ""
        for i, function in enumerate(functions, start=1):
            desc = function['description']
            function_info += f"{i}. {desc}\n"
        return function_info

    async def filter(self, query: str) -> List[dict]:
        function_info = self._get_function_info(self.functions)
        response = await client.chat.completions.create(
            model=GPT4,
            response_model=FunctionFiltering,
            max_retries=3,  # 在报错的情况下,会尝试一次重新把错误信息发送给 LLM,保证第二次输出正确
            messages=[
                {
                    "role": "system",
                    "content": dedent(f"""
                    As a large language model assistant, your task is:
                    1. Carefully read the following numbered function (interface) information:
                    {function_info}
                    2. Based on the user's query below, determine which of the above functions are irrelevant to the query.
                    3. From the functions above, find the numbers corresponding to the functions you consider completely irrelevant to the user's query, and return them as a list of integers.
                       Only include the corresponding numbers if you are very certain they are irrelevant. If every function might be relevant, return an empty list [].
                       Please provide your judgment directly, without any further explanation, in the following format: [3, 5, 7]

                    Take a deep breath, and here is user's query:
                    """)
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
        )  # type: ignore

        try:
            indices_to_remove = response.indices
        except ValueError:
            indices_to_remove = []

        if not indices_to_remove:
            return self.functions
        else:
            # 计算最多可以筛选掉的函数数量(总数的20%)
            max_remove_count = int(len(self.functions) * 0.2)
            # 如果大语言模型返回的无关函数编号超过最大筛选数量,只筛选掉前 max_remove_count 个
            if len(indices_to_remove) > max_remove_count:
                indices_to_remove = indices_to_remove[:max_remove_count]

            indices_to_keep = set(self.function_indices.keys()) - set(indices_to_remove)
            filtered_functions = [self.function_indices[i] for i in indices_to_keep]
            return filtered_functions

async def run(query, functions_list: list):
    parser = FilterFunctions(query, functions_list)
    return await parser()
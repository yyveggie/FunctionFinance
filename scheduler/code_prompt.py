import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import ast
import asyncio
from textwrap import dedent
from crawler import datetime_utils
from data_connection.data_handler import convert_to_json
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from config_loader import (
    GPT4O,
    GPT35,
    BASE_URL,
    OPENAI_API_KEY
)

openai_llm = ChatOpenAI(
    # base_url=BASE_URL,
    model=GPT4O,
    api_key=OPENAI_API_KEY,  # type: ignore
    temperature=0,
)

class LLM_Prompt_Code:
    def __init__(self, query, max_retries=2):
        self.code_llm = openai_llm
        self.query = query
        self.max_retries = max_retries

    async def __call__(self):
        return await self.code_executor(await self.code_prompt())  # type: ignore

    async def code_prompt(self):
        response = await asyncio.to_thread(self.code_llm.invoke, 
            [
                SystemMessage(
                    content=dedent(
                        f"You are a financial data retrieval expert, you only retrieve data by writing code."
                        f"You are familiar with the usage of some financial libraries' APIs, including but not limited to: 'yfinance', 'wallstreet', 'FinanceDatabase', 'baostock', 'akshare'."
                        f"- You should think in English"
                        f"- Be careful for logic errors, syntax errors, missing imports, variable declarations, mismatched brackets, and security vulnerabilities"
                        f"- Do not write code that requires api keys!"
                        f"- Don't forget that you need to import libraries before writing the subsequent code"
                        f"- The code MUST NOT contain any comments or any other non-code text, such as Markdown"
                        f"It MUST be Executable Python code."
                        f"- You must assign the result to a variable named 'result'"
                        f"You may need to know the current date: {datetime_utils.today()} for reference"
                    )
                ),
                HumanMessage(
                    content=dedent(
                        f"Write a executable python code without explanation or comments that can address my query: {self.query}."
                    ),
                ),
            ]
        )
        return response.content

    async def code_executor(self, content: str):
        # print(content)
        exec_globals = {}
        exec_locals = {}
        try:
            tree = ast.parse(content)
            fixed = ast.fix_missing_locations(tree)
            code = compile(fixed, "<ast>", "exec")
            for _ in range(self.max_retries):
                try:
                    exec(code, exec_globals, exec_locals)
                except Exception as e:
                    print(f"error: {e}")
                if "result" in exec_locals:
                    return {'subquery': self.query, 'value': convert_to_json(exec_locals['result'])}
                else:
                    continue
        except SyntaxError as e:
            return ""

async def run(query):
    try:
        parser = LLM_Prompt_Code(query)
        return await parser()
    except Exception as e:
        return ""

async def main():
    queries = [
        "不忙的话，帮我查一下谷歌的市盈率吧",
        "查一下阿里巴巴的资产负债表", 
        "搜一下苹果的新闻"
    ]
    
    tasks = [asyncio.create_task(run(query)) for query in queries]
    results = await asyncio.gather(*tasks)
    
    for query, result in zip(queries, results):
        print(query)
        print(result)
        print("————————————————————————————————————————————————————")

if __name__ == "__main__":
    asyncio.run(main())
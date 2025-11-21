# -*- coding: utf-8 -*-
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import codecs
from crawl4ai import WebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field

from config_loader import GPT4O, OPENAI_API_KEY

class OpenAIModelFee(BaseModel):
    answer_text: str = Field(..., description="当前用户所有回答的文本")

url = 'https://www.zhihu.com/people/da-meng-24-13/answers'
crawler = WebCrawler()
crawler.warmup()

result = crawler.run(
        url=url,
        word_count_threshold=1,
        extraction_strategy= LLMExtractionStrategy(
            provider= "openai/gpt-4o", api_token = OPENAI_API_KEY, 
            schema=OpenAIModelFee.schema(),
            extraction_type="schema",
            instruction="""抽取所有该用户的回答文本"""
        ),            
        bypass_cache=True,
    )

decoded_text = codecs.decode(result.extracted_content, 'unicode_escape')
print(decoded_text)
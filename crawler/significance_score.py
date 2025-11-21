import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import json
import datetime
from typing import List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from config_loader import OPENAI_API_KEY, GPT4O
from pydantic import BaseModel, ValidationError, field_validator
from string import Template

base_prompt = """
You are an AI assistant for stock news evaluation. In a moment, you will receive a piece of news about a particular stock. The news was published on ${create_time}, and the current time is ${current_time}. Please read the news carefully and then rate it based on the following criteria:

1. Relevance: Assess the relevance of the news to the target company/industry. News directly related to the company's fundamentals should receive a higher score.

2. Impact: Evaluate the potential impact of the news on the company's future financial performance, competitiveness, and reputation. News with a greater impact should receive a higher score.

3. Timeliness: Gauge how recent the news is compared to the current time. Generally, newer information tends to have a greater influence.

4. Uniqueness: Assess the uniqueness of the news and whether it discloses previously unknown information. Unique and significant positive or negative news may lead to greater stock price fluctuations.

5. Sentiment: Based on your understanding, determine whether the news is positive or negative, as this will influence the direction of stock price movement.

6. Scope: Evaluate the scope of influence of the news – whether it affects only the individual company, the industry, the market, or even the macroeconomy. News with a broader scope should receive a higher score.

7. Potential: Assess whether the event reported in the news might trigger a chain reaction and have a profound impact on the medium to long-term trends of the company and industry.

Please rate each criterion on a scale of 1-10, with 1 being the weakest and 10 being the strongest (For 'Sentiment', '5' is neutral).
"""

json_output_prompt = """  
Then, output the results in the following JSON format:

{
  "Relevance": x,
  "Impact": x,
  "Timeliness": x, 
  "Uniqueness": x,
  "Sentiment": x,
  "Scope": x,
  "Potential": x
}

No need for any extra explanation, just json output.
"""

class ArticleScore(BaseModel):
    Relevance: int
    Impact: int 
    Timeliness: int
    Uniqueness: int
    Sentiment: int
    Scope: int
    Potential: int

    @field_validator('*')
    def check_scores(cls, v):
        if not 1 <= v <= 10:
            raise ValueError(f"Score {v} must be between 1 and 10")
        return v

class AgentState(TypedDict):
    content: str
    messages: List[HumanMessage]
    scores: ArticleScore

class ArticleScorer:
    def __init__(self):
        self.model = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=GPT4O,
            temperature=0,
        )
        self.prompt_template = base_prompt + json_output_prompt
        self.parser = PydanticOutputParser(pydantic_object=ArticleScore)
        self.graph = self._create_graph()
        self.article_count = 0
            
    def _call_scorer(self, state):
        content = state["content"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.article_count % 10 == 0:
            self.formatted_prompt = Template(self.prompt_template).substitute(create_time="unknown", current_time=current_time)
        
        response = self.model.invoke([
            {"role": "system", "content": self.formatted_prompt},
            {"role": "user", "content": content}
        ])

        try:
            scores = self.parser.parse(response.content).dict()  # 使用对应的输出解析器解析响应内容,并转换为字典
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"Error in parsing response: {e}") 
            scores = {}  # 发生错误时,返回一个空的分数字典
        return {"scores": scores}

    def _should_continue(self, state):
        return False

    def _create_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("scorer", self._call_scorer)
        graph.set_entry_point("scorer")
        graph.add_conditional_edges(
            "scorer",
            lambda state: self._should_continue(state),
            {
                True: "scorer",
                False: END,
            }
        )
        return graph.compile()

    def score_articles(self, contents: List[str]):
        scores = []
        for content in contents:
            initial_message = HumanMessage(content=content)
            state = {"content": content, "messages": [initial_message]}
            result = self.graph.invoke(state)
            scores.append(result["scores"])
            self.article_count += 1
        return scores

if __name__ == "__main__":
    scorer = ArticleScorer()
    contents = [
        "Alibaba Group announced a strategic cooperation agreement with Ant Group.",
        "Tesla's stock price surged after the company reported record deliveries.",
    ]
    scores = scorer.score_articles(contents)
    print(scores)
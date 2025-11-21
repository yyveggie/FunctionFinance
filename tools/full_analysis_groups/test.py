import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import time
import json
from typing import Dict, List, TypedDict, Sequence
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.prebuilt import ToolExecutor
from enum import Enum
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from textwrap import dedent
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from config_loader import (
    CALLING_LLM_API_KEY_2, 
    CALLING_LLM, 
    GPT35_LLM, 
    GPT35_API_KEY_3,
    BASE_URL
)

system_prompt_initial_sentinel = dedent(
    f"As a financial news sentinel, your task is to carefully assess each piece of financial news presented to you and determine if it contains valuable insights or information that could potentially impact the market or provide meaningful predictions or analysis."
    f"To make this determination, you should look for the presence of any of the following types of information in the news:"
    f"1. Indications of market sentiment, such as significant corporate events, key economic indicators, major geopolitical developments, or other news that could sway investor confidence or market direction."
    f"2. Predictive insights, including forecasts, projections, or expectations for future market movements, economic trends, company performance, or other forward-looking analysis."
    f"3. In-depth analytical insights that provide a detailed examination of market trends, dissection of company financials, commentary from industry experts, or other rigorous analysis of financial topics."
    f"4. Any other information that you deem to be of significant potential impact or value in understanding, predicting, or making decisions in financial markets."
    f"When you receive a piece of financial news, carefully analyze its content for the presence of any such valuable information. If the news contains insights worth recording, respond with 'TRUE'. If the news does not contain any notable insights, respond with 'FALSE'."
    f"Please limit your response to only 'TRUE' or 'FALSE' without providing any additional explanation or information."
)

system_prompt_initial_knowledge_master = dedent(
    f"As a financial news insight extractor, your role is to meticulously analyze pieces of financial news that have been identified as containing valuable information, and to extract and summarize the key insights from these articles."
    f"For each piece of news, carefully identify and isolate the most important and actionable pieces of information, focusing on insights that fall into the following categories:"
    f"1. Market Sentiment: Information that reflects or could influence overall market sentiment, such as significant corporate events, economic indicators, geopolitical developments, or other news that could sway investor confidence or market direction."
    f"2. Predictive Insights: Forward-looking analysis, including forecasts, projections, or expectations for future market movements, economic trends, company performance, or other predictive insights."
    f"3. Analytical Insights: Detailed examination of market trends, dissection of company financials, commentary from industry experts, or other rigorous analysis of financial topics."
    f"4. Economic Indicators: Key data points or trends that provide insight into the state or direction of the economy, such as GDP growth, inflation rates, employment figures, or other macroeconomic indicators."
    f"5. Corporate Events: Significant developments or announcements related to specific companies, such as earnings reports, mergers and acquisitions, leadership changes, strategic shifts, or other notable corporate news."
    f"6. Regulatory Changes: Changes to financial regulations, government policies, or legal rulings that could impact financial markets or specific industries."
    f"7. Geopolitical Events: Major global political developments, international relations, or geopolitical shifts that could have economic or financial implications."
    f"8. Market Trends: Identification of notable trends, patterns, or movements in specific markets, sectors, or asset classes."
    f"9. Expert Opinions: Insightful commentary, analysis, or opinions from respected financial experts, analysts, or industry leaders."
    f"10. Technical Analysis: Insights derived from the analysis of market data, charts, or technical indicators that could signal potential market movements or trends."
    f"For each insight you identify, provide a clear and concise summary, focusing on the key points and implications. Aim to extract and summarize all significant insights from the given piece of news."
    f"When you have finished extracting insights from the most recent piece of news, respond with 'EXTRACTION COMPLETE', followed by your summarized insights categorized under the appropriate insight type headings. If no notable insights are found in the given piece of news, simply respond with 'NO INSIGHTS FOUND'."
)


class FinancialNewsCategory(str, Enum):
    MarketSentiment = "Market Sentiment"
    PredictiveInsight = "Predictive Insight"
    AnalyticalInsight = "Analytical Insight"
    EconomicIndicator = "Economic Indicator"
    CorporateEvent = "Corporate Event"
    RegulatoryChange = "Regulatory Change"
    GeopoliticalEvent = "Geopolitical Event"
    MarketTrend = "Market Trend"
    ExpertOpinion = "Expert Opinion"
    TechnicalAnalysis = "Technical Analysis"


class AddFinancialNewsInsight(BaseModel):
    insight: str = Field(
        ...,
        description="Condensed piece of financial news insight to be saved for future reference.",
    )
    category: FinancialNewsCategory = Field(
        ..., 
        description="Financial news category that this insight belongs to"
    )


def add_financial_news_insight(
    insight: str,
    category: str,
) -> dict:
    print("Adding Financial News Insight: ",
          insight, category)
    return {"status": "Success", "message": "Financial news insight added"}


tool_add_financial_news_insight = StructuredTool.from_function(
    func=add_financial_news_insight,
    name="Financial_News_Insight_Adder",
    description="Add a piece of financial news insight",
    args_schema=AddFinancialNewsInsight,
)


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    insights: Sequence[str]
    contains_information: str


def call_sentinel(state):
    messages = state["messages"]
    response = state["sentinel_runnable"].invoke(
        messages)
    return {"contains_information": "TRUE" in response.content and "yes" or "no"}


def should_continue(state):
    last_message = state["messages"][-1]
    if "tool_calls" not in last_message.additional_kwargs:
        return "end"
    else:
        return "continue"


def call_knowledge_master(state):
    messages = state["messages"]
    insights = state["insights"]
    response = state["knowledge_master_runnable"].invoke(
        {"messages": messages, "insights": insights}
    )
    return {"messages": messages + [response]}


def call_tool(state):
    messages = state["messages"]
    insights = state.get("insights", [])
    last_message = messages[-1]
    new_insights = list(insights)

    for tool_call in last_message.additional_kwargs["tool_calls"]:
        action = ToolInvocation(
            tool=tool_call["function"]["name"],
            tool_input=json.loads(tool_call["function"]["arguments"]),
            id=tool_call["id"],
        )

        response_dict = state["tool_executor"].invoke(
            action)  

        insight_info = str(action.tool_input)
        if insight_info != "":
            new_insights.append(insight_info)

    print("Current insights:")
    for i, insight in enumerate(new_insights, start=1):
        print(f"{i}. {insight}")

    return {"messages": messages, "insights": new_insights}


class FinancialNewsInsightExtractor:
    def __init__(self):
        self.insight_base_file = "./data_connection/insight_base.json"
        self.insight_base: Dict[str, List[str]] = self.load_insight_base()

        self.agent_tools = [tool_add_financial_news_insight]
        self.tool_executor = ToolExecutor(self.agent_tools)

        sentinel_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                system_prompt_initial_sentinel),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Remember, only respond with TRUE or FALSE. Do not provide any other information."),
        ])
        knowledge_master_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                system_prompt_initial_knowledge_master),
            MessagesPlaceholder(variable_name="messages"),
        ])

        tools = [convert_to_openai_function(t) for t in self.agent_tools]

        self.sentinel_runnable = sentinel_prompt | ChatOpenAI(
            # base_url=BASE_URL,
            temperature=0,
            model=GPT35_LLM,
            api_key=GPT35_API_KEY_3, # type: ignore
        )
        self.knowledge_master_runnable = knowledge_master_prompt | ChatOpenAI(
            base_url=BASE_URL,
            temperature=0.5,
            model=CALLING_LLM,
            api_key=CALLING_LLM_API_KEY_2, # type: ignore
        ).bind_tools(
            tools)

    def load_insight_base(self) -> Dict[str, List[str]]:
        if os.path.exists(self.insight_base_file):
            with open(self.insight_base_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}


    def process_financial_news(self, news_id: str, news_content: str):
        self.insight_base.setdefault(news_id, [])

        messages = [HumanMessage(content=news_content)]
        contains_information = False
        new_insights = []

        response = self.sentinel_runnable.invoke({"messages": messages})
        contains_information = "TRUE" in response.content

        if contains_information:
            raw_insights = self.insight_base.get(news_id, [])
            insights = []

            for insight in raw_insights:
                insights.append(insight)

            response = self.knowledge_master_runnable.invoke(
                {"messages": messages, "insights": insights}
            )
            messages += [response]
            last_message = messages[-1]

            if "tool_calls" in last_message.additional_kwargs:
                for tool_call in last_message.additional_kwargs["tool_calls"]:
                    action = ToolInvocation(
                        tool=tool_call["function"]["name"],
                        tool_input=json.loads(tool_call["function"]["arguments"]),
                        id=tool_call["id"],
                    )
                    response_dict = self.tool_executor.invoke(action)
                    if isinstance(action.tool_input, dict):
                        new_insights.append(action.tool_input)

            self.save_insight_base(news_id, new_insights)
        return new_insights

    
    def save_insight_base(self, news_id: str, new_insights: List[Dict[str, str]]):
        self.insight_base = self.load_insight_base()
        if news_id not in self.insight_base:
            self.insight_base[news_id] = []

        timestamp = time.time()
        for insight in new_insights:
            self.insight_base[news_id].append(
                {"timestamp": timestamp, **insight})  
        with open(self.insight_base_file, "w", encoding="utf-8") as f:
            json.dump(self.insight_base, f, ensure_ascii=False, indent=2)
    

if __name__ == "__main__":
    news_id = "test_news_1"
    news_content = "Federal Reserve Chairman Jerome Powell signaled that the central bank is likely to raise interest rates by a half percentage point at its next meeting in May, stepping up efforts to curb inflation. The move would mark the first half-point rate increase since 2000 and follow a quarter-point rise in March, the first increase since 2018. 'It is appropriate in my view to be moving a little more quickly,' Mr. Powell said in a discussion of the global economy at the meetings of the International Monetary Fund. 'I also think there's something in the idea of front-end loading' moves if appropriate, he said in a discussion of the global economy at the meetings of the International Monetary Fund."
    insight_extractor = FinancialNewsInsightExtractor()
    print(insight_extractor.process_financial_news(news_id, news_content))

graph = StateGraph(AgentState)

graph.add_node("sentinel", call_sentinel)
graph.add_node("knowledge_master", call_knowledge_master)
graph.add_node("action", call_tool)

graph.set_entry_point("sentinel")

graph.add_conditional_edges(
    "sentinel",
    lambda x: x["contains_information"],
    {
        "yes": "knowledge_master",
        "no": END,
    },
)
graph.add_conditional_edges(
    "knowledge_master",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

graph.add_edge("action", END)

app = graph.compile()
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from datetime import datetime
from typing import List, Sequence, TypedDict
from langchain_openai.chat_models import ChatOpenAI
from data_connection.mongodb import MongoConnection
from config_loader import (
    OPENAI_API_KEY, 
    BASE_URL, 
    ZEN_API_KEY, 
    GPT4,
    GPT4O,
)
from textwrap import dedent
from langchain.pydantic_v1 import BaseModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation, ToolExecutor
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.tools import StructuredTool
from langchain_core.messages import HumanMessage, BaseMessage
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
import json

class Triple(BaseModel):
    subject: str
    predicate: str
    object: str
    summary: str
    
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    triples: List[Triple]

def call_sentinel(state):
    messages = state["messages"]
    response = state["sentinel_runnable"].invoke({"messages": messages})
    return {"contains_information": "TRUE" in response.content}

def should_continue(state):
    last_message = state["messages"][-1]
    if "tool_calls" not in last_message.additional_kwargs:
        return "end"
    else:
        return "continue"

def call_knowledge_extractor(state):
    messages = state["messages"]
    triples = state["triples"]
    response = state["extraction_runnable"].invoke(
        {"messages": messages, "existing_triples": triples}
    )
    return {"messages": messages + [response]}

def call_tool(state):
    messages = state["messages"]
    triples = state.get("triples", [])
    last_message = messages[-1]
    new_triples = list(triples)

    for tool_call in last_message.additional_kwargs["tool_calls"]:
        action = ToolInvocation(
            tool=tool_call["function"]["name"],
            tool_input=tool_call["function"]["arguments"],
            id=tool_call["id"],
        )
        new_triples.append(action.tool_input)

    return {"messages": messages, "triples": new_triples}

class StockKnowledgeExtractor:
    def __init__(self, mongo_db_name: str, mongo_host: str, mongo_port: int):
        self.mongo_connection = MongoConnection(db_name=mongo_db_name, host=mongo_host, port=mongo_port)
        
        self.sentinel_runnable = self.create_sentinel_runnable()
        self.extraction_runnable = self.create_extraction_runnable()
        self.tool_executor = ToolExecutor(self.create_tools())

        self.reset_counter = 0
        
    def create_sentinel_runnable(self):
        system_prompt_initial_sentinel = dedent(
            f"Your job is to assess a piece of stock-related news to determine if it contains any information that could potentially impact the company's stock price or performance."
            f"This includes events such as financial reports, mergers and acquisitions, changes in equity structure, executive personnel changes, major business decisions, legal issues, as well as market sentiment, personal opinions, and other factors that may indirectly influence the stock price."  
            f"The information should be extracted in the form of triples representing entities, relationships, and attributes relevant to the stock."
            f"When you receive a piece of news, you perform the following steps:"
            f"1. Analyze the news for stock-related information."  
            f"2. If it contains any information worth recording, return TRUE. If not, return FALSE."
            f"You should ONLY RESPOND WITH TRUE OR FALSE. Absolutely no other information should be provided."
            f"Take a deep breath, think step by step, and then analyze the following news article:"
        )

        sentinel_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt_initial_sentinel),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Remember, only respond with TRUE or FALSE. Do not provide any other information."),
        ])

        return sentinel_prompt | ChatOpenAI(
            api_key=OPENAI_API_KEY, 
            model=GPT4O,
            temperature=0,
        )

    def create_extraction_runnable(self):
        system_prompt_initial_extraction = dedent(
            f"You are an expert in extracting valuable knowledge triples from stock-related news."
            f"Your task is to create a comprehensive knowledge base about companies, their financial performance, business activities, events that could directly influence their stock prices, as well as market sentiment, personal opinions, and other factors that may indirectly affect stock prices."
            f"The knowledge base should consist of triples representing entities, relationships, and attributes relevant to stocks, such as:"
            f"- <Company A, announces, quarterly earnings>"
            f"- <Company B, acquires, Company C>"
            f"- <Company D, appoints, new CEO>"
            f"- <Regulatory Body, fines, Company E>"
            f"- <Analyst X, gives buy rating, Company Y>"
            f"- <Market sentiment, turns positive, Company Z>"  
            f"When you receive a piece of news, perform the following steps:"
            f"1. Analyze the news article for stock-related information, including both direct and indirect factors."
            f"2. Extract relevant entities, relationships, and attributes in the form of triples."
            f"3. For each new triple, write a concise summary to provide context."
            f"4. Call the relevant tool to save the new triples and their summaries to the knowledge base."
            f"Please extract important knowledge triples from the following news article. Each triple should consist of a subject, predicate, object, and summary, enclosed in <>."
            f"Ensure that each triple has all the required fields: subject, predicate, object, and summary. If any field is missing, replace it with 'N/A'."
            f"News text:"
        )

        extraction_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt_initial_extraction),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        tools = [
            StructuredTool.from_function(
                func=self.add_triple,
                name="add_triple",
                description="Add a new triple to the knowledge base",
                args_schema=Triple,
            ),
        ]

        return extraction_prompt | ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=GPT4O
        ).bind_tools(
            [convert_to_openai_function(t) for t in tools])
        
    def create_tools(self):
        return [
            StructuredTool.from_function(
                func=self.add_triple,
                name="add_triple",
                description="Add a new triple to the knowledge base",
                args_schema=Triple,
            ),
        ]
    
    def process_news(self, news_list: List[str], batch_size: int = 10):
        all_triples = []
        self.reset_counter += 1
        
        if self.reset_counter % 10 == 0:
            self.reset_system_prompts()
        
        for i in range(0, len(news_list), batch_size):
            batch_news = news_list[i:i+batch_size]
            for news in batch_news:
                messages = [HumanMessage(content=news)]
                if not messages:
                    continue  # 如果没有消息,跳过该批次的处理
                    
                # 使用 self.sentinel_runnable 判断是否包含信息
                sentinel_response = self.sentinel_runnable.invoke({"messages": messages})
                contains_information = "TRUE" in sentinel_response.content
                
                if contains_information:
                    # 使用 self.extraction_runnable 提取三元组
                    extraction_response = self.extraction_runnable.invoke(
                        {"messages": messages, "existing_triples": all_triples}
                    )
                    
                    # 从 extraction_response 中提取新的三元组
                    if "tool_calls" in extraction_response.additional_kwargs:
                        for tool_call in extraction_response.additional_kwargs["tool_calls"]:
                            action = ToolInvocation(
                                tool=tool_call["function"]["name"],
                                tool_input=tool_call["function"]["arguments"],
                                id=tool_call["id"],
                            )
                            # 将字符串形式的字典转换为真正的字典对象
                            triple_dict = json.loads(action.tool_input)
                            all_triples.append(triple_dict)
        return all_triples

    def add_triple(self, triple: Triple) -> dict:
        print(f"Adding triple: {triple}")
        data = {
            "subject": triple.subject,
            "predicate": triple.predicate,
            "object": triple.object,
            "summary": triple.summary,  # 确保每个三元组都有摘要
        }
        return {"status": "Success", "message": "Triple added"}

    def save_to_mongodb(self, triples: List[dict]):
        today = datetime.today().strftime("%Y%m%d")
        collection_name = today

        for triple in triples:
            self.mongo_connection.save_data(collection_name, "", triple)
            
    def reset_system_prompts(self):
        self.sentinel_runnable = self.create_sentinel_runnable()
        self.extraction_runnable = self.create_extraction_runnable()
        
    def extract_and_save(self, news_list):
        all_triples = self.process_news(news_list)
        self.save_to_mongodb(all_triples)
        return all_triples
      
if __name__ == "__main__":
    mongo_db_name = "ALIBABA"
    mongo_host = "localhost"
    mongo_port = 27018
    
    news_list = [
        "Alibaba Group announced a strategic cooperation agreement with Ant Group.",
        "Alibaba's revenue in the first quarter of 2022 increased by 30% year-on-year.",
        "Some analysts believe that Alibaba's stock is currently undervalued and give it a buy rating.",
        "Alibaba announced the appointment of Daniel Zhang as the new CEO, and Eric Jing will step down as CEO.",
        "Alibaba denied rumors of selling Ant Group shares."
    ]
    
    extractor = StockKnowledgeExtractor(mongo_db_name, mongo_host, mongo_port)
    print(extractor.extract_and_save(news_list))

graph = StateGraph(AgentState)

graph.add_node("sentinel", call_sentinel)
graph.add_node("knowledge_master", call_knowledge_extractor)
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
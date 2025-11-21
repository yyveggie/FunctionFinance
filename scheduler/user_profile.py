import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import os
import time
import json
from enum import Enum
from typing import Dict, List, TypedDict, Sequence, Optional
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.prebuilt import ToolExecutor
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from textwrap import dedent
from langchain_openai.chat_models import ChatOpenAI
from langchain_groq.chat_models import ChatGroq
from langchain_together.chat_models import ChatTogether
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from config_loader import (
    GROQ_LLAMA3_8B,
    OPENAI_API_KEY,
    GPT35,
    GPT4O,
    GROQ_API_KEY,
    GROQ_LLAMA3_70B,
    GROQ_MIXTRAL_8x7B,
    GROQ_GEMMA_7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B,
    TOGETHER_LLAMA3_70B,
)

system_prompt_initial_sentinel = dedent(
    f"Your job is to assess a brief chat history to determine if the conversation contains any details about a users' profile, attributes, financial habits, financial preferences."
    f"You are part of a team building a knowledge base regarding users' financial attributes to assist in providing highly customized financial analyses across various sectors and products, including stocks, futures, bonds, options, forex, currencies, funds, indices, macroeconomics, cryptocurrencies, and industries."
    f"You play a critical role in assessing the message to determine if it contains any information worth recording in the knowledge base."
    f"You are only interested in the following categories of information:"
    f"1. Investment preferences and experiences across our analysis services (e.g., an interest in forex trading, cryptocurrency investments)."
    f"2. Risk tolerance (e.g., high risk in stocks or low risk in bonds)."
    f"3. Financial goals related to the available financial analysis services (e.g., long-term growth in funds, hedging with options)."
    f"4. User attributes (e.g., name, nickname, age, gender, occupation, employer, department, income, liabilities, assets, credit score)."
    f"5. Specific interests or inquiries about market sectors or financial products (e.g., bullish on technology stocks, looking into gold futures)."
    f"6. Any additional relevant financial behaviors, preferences, or requests for analysis not explicitly listed above."
    f"When you receive a message, you perform a sequence of steps consisting of:"
    f"1. Analyze the message for information."
    f"2. If it has any information worth recording, return TRUE. If not, return FALSE."
    f"You should ONLY RESPOND WITH TRUE OR FALSE. Absolutely no other information should be provided."
    f"Take a deep breath, think step by step, and then analyze the following message:"
)

system_prompt_initial_knowledge_master = dedent(
    f"You are a supervisor managing a team of knowledge experts."
    f"Your team's job is to create a perfect knowledge base about users' financial habits and preferences to assist in providing highly customized financial analyses."
    f"Sometimes if there is no financial habits or preference information to record, some user attributes can also be recorded."
    f"The knowledge base should ultimately consist of many discrete pieces of information that add up to a detailed financial persona (e.g. 'Prefers investing in stocks', 'High risk tolerance', 'Aims for retirement by 50', 'Annual income of $100,000', 'Owns real estate')."
    f"Every time you receive a message, It must have information worth recording:) You have to extract some knowledge from it."
    f"A message may contain multiple pieces of information that should be saved separately."
    f"You are only interested in the following categories of information:"
    f"1. Investment preferences (e.g., prefers stocks or bonds) - These help tailor investment strategies."
    f"2. Risk tolerance (e.g., high risk or low risk) - Crucial for aligning with the user's comfort with market volatility."
    f"3. Financial goals (e.g., retirement planning, buying a house) - Guides the financial planning process."
    f"4. User attributes (e.g., name, age, gender, occupation, income, liabilities, assets, credit score) - Provides a holistic view of the user's financial standing."
    f"5. Specific interests in financial markets or products (e.g., interested in cryptocurrency, looking into gold futures) - Helps focus the analysis on relevant sectors."
    f"When you receive a message, you perform a sequence of steps consisting of:"
    f"1. Analyze the most recent Human message for information. You will see multiple messages for context, but we are only looking for new information in the most recent message."
    f"2. Compare this to the knowledge you already have."
    f"3. Determine if this is new knowledge, an update to old knowledge that now needs to change, or should result in deleting information that is not correct. It's possible that an investment preference has changed, or that a financial goal has been achieved or modified - those examples would require an update."
    f"4. Call the right tools to save the new information, update existing information, or delete incorrect information. Respond with DONE after calling the tools."
    f"Here are the existing bits of information that we have about the user."
    f"```"
    "{memories}"
    f"```"
    f"If you identify multiple pieces of information, call all the relevant tools at once. You only have one chance to call tools."
    f"For example:"
        f"Input: 'I want to retire by age 50 with $2 million saved up. I currently make $100k per year.'"
        f"Think: 'This input has obvious financial attributes and preferences that can be recorded'"
        f"Input: 'My name is John and I am 17 years old.'"
        f"Think: 'Although this input does not record financial preferences, it can record the user's attributes: name and age. Both age and name can be used as a form of user analysis.'"
    f"Take a deep breath, think step by step, and then analyze the following message:"
)

class FinancialCategory(str, Enum):
    InvestmentPreference = "Investment Preference"
    RiskTolerance = "Risk Tolerance"
    FinancialGoal = "Financial Goal"
    UserAttribute = "User Attribute"
    MarketInterest = "Market Interest"

class Action(str, Enum):
    Create = "Create"
    Update = "Update"
    Delete = "Delete"

class AddFinancialKnowledge(BaseModel):
    knowledge: str = Field(
        ...,
        description="Condensed bit of financial knowledge to be saved for future reference. Format: [attribute]: [detail] (e.g., 'Risk Tolerance: Low', 'Interested in: Cryptocurrency')",
    )
    knowledge_old: Optional[str] = Field(
        None,
        description="If updating or deleting a record, the complete, exact phrase that needs to be modified",
    )
    category: FinancialCategory = Field(
        ..., 
        description="Financial category that this knowledge belongs to"
    )
    action: Action = Field(
        ...,
        description="Whether this knowledge is adding a new record, updating a record, or deleting a record",
    )

def modify_financial_knowledge(
    knowledge: str,
    category: str,
    action: str,
    knowledge_old: str = "",
) -> dict:
    # print("Modifying Financial Knowledge: ",
    #       knowledge, knowledge_old, category, action)
    return {"status": "Success", "message": "Financial knowledge modified"}

tool_modify_financial_knowledge = StructuredTool.from_function(
    func=modify_financial_knowledge,
    name="Financial_Knowledge_Modifier",
    description="Add, update, or delete a bit of financial knowledge",
    args_schema=AddFinancialKnowledge,
)

class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    memories: Sequence[str]
    contains_information: str

def call_sentinel(state):
    messages = state["messages"]
    response = state["sentinel_runnable"].invoke(
        messages)  # 使用初始化后的 sentinel_runnable
    return {"contains_information": "TRUE" in response.content and "yes" or "no"}

def should_continue(state):
    last_message = state["messages"][-1]
    if "tool_calls" not in last_message.additional_kwargs:
        return "end"
    else:
        return "continue"

def call_knowledge_master(state):
    messages = state["messages"]
    memories = state["memories"]
    response = state["knowledge_master_runnable"].invoke(
        {"messages": messages, "memories": memories}
    )
    return {"messages": messages + [response]}

def call_tool(state):
    messages = state["messages"]
    memories = state.get("memories", [])
    last_message = messages[-1]
    new_memories = list(memories)
    for tool_call in last_message.additional_kwargs["tool_calls"]:
        action = ToolInvocation(
            tool=tool_call["function"]["name"],
            tool_input=json.loads(tool_call["function"]["arguments"]),
            id=tool_call["id"],
        )
        response_dict = state["tool_executor"].invoke(
            action)  # 使用初始化后的 tool_executor
        knowledge_info = str(action.tool_input)
        if knowledge_info != "":
            new_memories.append(knowledge_info)
    print("Current knowledge base:")
    for i, memory in enumerate(new_memories, start=1):
        print(f"{i}. {memory}")
    return {"messages": messages, "memories": new_memories}

class FinancialKnowledgeBase:
    def __init__(self):
        self.knowledge_base_file = "./data_connection/knowledge_base.json"
        self.knowledge_base: Dict[str, List[str]] = self.load_knowledge_base()
        self.agent_tools = [tool_modify_financial_knowledge]
        self.tool_executor = ToolExecutor(self.agent_tools)
        # Pre-define prompts
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

        self.sentinel_runnable = sentinel_prompt | ChatTogether(
            # base_url=BASE_URL,
            temperature=0,
            model=TOGETHER_LLAMA3_8B,
            api_key=TOGETHER_API_KEY, # type: ignore
        )
        # Pre-initialize runnables with prompts
        self.knowledge_master_runnable = knowledge_master_prompt | ChatTogether(
            # base_url=BASE_URL,
            temperature=0,
            model=TOGETHER_LLAMA3_8B,
            api_key=TOGETHER_API_KEY, # type: ignore
            
        ).bind_tools(
            tools)

    def load_knowledge_base(self) -> Dict[str, List[str]]:
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    def process_user_input(self, user_id: str, user_input: str):
        self.knowledge_base.setdefault(user_id, [])

        messages = [HumanMessage(content=user_input)]
        contains_information = False
        new_memories = []

        response = self.sentinel_runnable.invoke({"messages": messages})
        contains_information = "TRUE" in response.content

        if contains_information:
            raw_memories = self.knowledge_base.get(user_id, [])
            memories = []

            for memory in raw_memories:
                memories.append(memory)

            response = self.knowledge_master_runnable.invoke(
                {"messages": messages, "memories": memories}
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
                        new_memories.append(action.tool_input)
                    else:
                        print(f"Unexpected format of tool input: {action.tool_input}")

            self.save_knowledge_base(user_id, new_memories)
        return new_memories

    def save_knowledge_base(self, user_id: str, new_memories: List[Dict[str, str]]):
        self.knowledge_base = self.load_knowledge_base()
        if user_id not in self.knowledge_base:
            self.knowledge_base[user_id] = []

        timestamp = time.time()
        for memory in new_memories:
            self.knowledge_base[user_id].append(
                {"timestamp": timestamp, **memory})  # type: ignore
        # 将更新后的知识库写回文件
        with open(self.knowledge_base_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    user_id = "test_nightingale"
    knowledge_base = FinancialKnowledgeBase()
    user_input = "我对投资加密货币很感兴趣,但风险承受能力较低。我的主要财务目标是在50岁退休。"
    # user_input = '我的月收入有3000'
    print(knowledge_base.process_user_input(user_id, user_input))

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

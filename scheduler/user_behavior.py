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
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from config_loader import (
    OPENAI_API_KEY,
    GPT35,
    GPT4O,
    GROQ_API_KEY,
    GROQ_LLAMA3_70B,
    GROQ_LLAMA3_8B
)

system_prompt_initial_sentinel = dedent(
    f"Your task is to assess a brief chat history to determine if the conversation contains any details about the user's psychological characteristics and biases in the context of behavioral finance."
    f"You are part of a team building a knowledge base about users' behavioral finance psychology to assist in providing highly personalized investment advice and financial decision support."
    f"You play a critical role in assessing the message to determine if it contains any information worth recording in the knowledge base."
    f"You are only interested in the following categories of information:"
    f"1. Mental Accounting: Does the user divide money into different mental accounts and adopt different investment risk attitudes for different accounts?"
    f"2. Loss Aversion: Is the user more sensitive to losses than to gains?"
    f"3. Endowment Effect: Does the user tend to overvalue the investments they already own?"
    f"4. Herd Behavior: Is the user easily influenced by the investment behavior of the masses?"
    f"5. Disposition Effect: Does the user tend to sell profitable investments too early while holding on to losing investments?"
    f"6. Overconfidence: Is the user overconfident in their investment abilities, tending to overestimate their knowledge and control over the market?"
    f"7. Anchoring: Is the user easily swayed by a reference point (e.g., historical high) when making investment judgments?"
    f"When you receive a message, you perform a sequence of steps consisting of:"
    f"1. Analyze the message for information."
    f"2. If it has any information worth recording, return TRUE. If not, return FALSE."
    f"You should ONLY RESPOND WITH TRUE OR FALSE. Absolutely no other information should be provided."
    f"Take a deep breath, think step by step, and then analyze the following message:"
)

system_prompt_initial_knowledge_master = dedent(
    f"You are a supervisor managing a team of knowledge experts."
    f"Your team's job is to create a perfect knowledge base about users' behavioral finance psychological factors to assist in providing highly personalized investment advice."
    f"The knowledge base should ultimately consist of many discrete pieces of information that add up to a detailed behavioral finance psychological profile (e.g., 'Easily influenced by popular investment trends', 'Overestimates own investment abilities', 'Tends to sell profitable investments too early')."
    f"Every time you receive a message, you must extract some information worth recording from it. There will be no case where there is no extractable information."
    f"A message may contain multiple pieces of information that should be saved separately."
    f"You are only interested in the following categories of information:"
    f"1. Mental Accounting - This helps understand the user's psychological division of funds and differences in risk preferences."
    f"2. Loss Aversion - This helps assess the user's attitude towards risk and loss."
    f"3. Endowment Effect - This helps determine the user's tendency to overvalue their held investments."
    f"4. Herd Behavior - This helps evaluate the user's attention and reaction to popular market trends."
    f"5. Disposition Effect - This helps predict the user's likely holding and disposition decision tendencies for winning and losing investments."
    f"6. Overconfidence - This helps judge the user's self-assessment bias and the risk of making mistakes."
    f"7. Anchoring - This helps analyze what reference benchmarks influence the user's decisions."
    f"When you receive a message, you perform a sequence of steps consisting of:"
    f"1. Analyze the most recent Human message for information. You will see multiple messages for context, but we are only looking for new information in the most recent message."
    f"2. Compare this to the knowledge you already have."
    f"3. Determine if this is new knowledge, an update to old knowledge that now needs to change, or should result in deleting information that is not correct. Psychological characteristics may change over time, such as changes in risk preferences, which require updating existing information."
    f"4. Call the right tools to save the new information, update existing information, or delete incorrect information. Respond with DONE after calling the tools."
    f"Here are the existing bits of information that we have about the user:"
    f"```"
    "{memories}"
    f"```"
    f"If you identify multiple pieces of information, call all the relevant tools at once. You only have one chance to call tools."
    f"For example:"
        f"Input: 'I'm used to dividing my money into three accounts: daily expenses, insurance, and investment, and managing them separately. I once had an investment that lost 20%, which made me very uncomfortable. Since then, I no longer dare to make high-risk investments.'"
        f"Think: 'This input explicitly mentions mental accounting and loss aversion, which is very valuable information.'"
        f"Input: 'I think I have a very good grasp of the market, so my stocks are usually fully invested.'"
        f"Think: 'This reflects an overconfidence mindset, which is worth recording.'"
    f"Take a deep breath, think step by step, and then analyze the following message:"
)

class BehavioralCategory(str, Enum):
    MentalAccounting = "Mental Accounting"
    LossAversion = "Loss Aversion" 
    EndowmentEffect = "Endowment Effect"
    HerdBehavior = "Herd Behavior"
    DispositionEffect = "Disposition Effect"
    Overconfidence = "Overconfidence" 
    Anchoring = "Anchoring"


class Action(str, Enum):
    Create = "Create"
    Update = "Update"
    Delete = "Delete"

class AddBehavioralKnowledge(BaseModel):
    knowledge: str = Field(
        ...,
        description="Condensed bit of behavioral finance knowledge to be saved for future reference. Format: [psychological characteristic]: [detail] (e.g., 'Loss Aversion: Had a 20% loss experience once, no longer dares to make high-risk investments')",
    )
    knowledge_old: Optional[str] = Field(
        None,  
        description="If updating or deleting a record, the complete, exact phrase that needs to be modified",
    )
    category: BehavioralCategory = Field(
        ...,
        description="Behavioral finance category that this knowledge belongs to" 
    )
    action: Action = Field(
        ...,
        description="Whether this knowledge is adding a new record, updating a record, or deleting a record",
    )

def modify_behavioral_knowledge(
    knowledge: str,
    category: str, 
    action: str,
    knowledge_old: str = "",
) -> dict:
    # print("Modifying Behavioral Finance Knowledge: ",
    #       knowledge, knowledge_old, category, action)
    return {"status": "Success", "message": "Behavioral finance knowledge modified"} 


tool_modify_behavioral_knowledge = StructuredTool.from_function(
    func=modify_behavioral_knowledge,
    name="Behavioral_Knowledge_Modifier",
    description="Add, update, or delete a bit of behavioral finance knowledge", 
    args_schema=AddBehavioralKnowledge,
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


class BehaviorKnowledgeBase:
    def __init__(self):
        self.knowledge_base_file = "./data_connection/knowledge_base.json"
        self.knowledge_base: Dict[str, List[str]] = self.load_knowledge_base()

        self.agent_tools = [tool_modify_behavioral_knowledge]
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

        self.sentinel_runnable = sentinel_prompt | ChatGroq(
            temperature=0,
            model=GROQ_LLAMA3_8B,
            api_key=GROQ_API_KEY, # type: ignore
        )
        # Pre-initialize runnables with prompts
        self.knowledge_master_runnable = knowledge_master_prompt | ChatGroq(
            temperature=0.5,
            model=GROQ_LLAMA3_8B,
            api_key=GROQ_API_KEY, # type: ignore
            
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
    knowledge_base = BehaviorKnowledgeBase()
    user_input = "我对投资加密货币很感兴趣,但风险承受能力较低。我的主要财务目标是在50岁退休。我是个很自信的人"
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

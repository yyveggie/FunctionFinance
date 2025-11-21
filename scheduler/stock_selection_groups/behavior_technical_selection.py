import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_together import Together
from langchain_openai import ChatOpenAI
from textwrap import dedent
from scheduler.prompt_tips import self_improve, explain_why
from scheduler.callback import print_agent_output
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from scheduler.tools import vision_tools
from pydantic import BaseModel, Field
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_HAIKU,
    GROQ_API_KEY,
    GROQ_MIXTRAL_8x7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B,
    OPENAI_API_KEY,
    GPT4O
)
import time

haiku = ChatAnthropic(
    model_name=CLAUDE_HAIKU,
    api_key=CLAUDE_API_KEY, # type: ignore
    temperature=0.5,
)

llm_1 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_2 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_3 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_4 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_5 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_6 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

gpt4o = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY,
)

financial_indicators_tool = FileReadTool("./BABA_results.json")

class Output(BaseModel):
    recommendations: list[dict] = Field(description='A list containing three dictionaries, giving the final confidence level and reason for each recommendation.')

def behavior_technical_group(stock):
    behavioral_financial_analysis_agent = Agent(
            role="行为金融分析师",
            goal="根据金融数据或指标分析市场心理",
            tools=[financial_indicators_tool] + vision_tools.tools(),
            backstory=dedent(
                f'''
                你是最好的股市行为分析师。你从不关注技术分析或基本面分析，而是相信了解市场心理可以做出更好的预测。无论给你什么财务数据或指标，你只会从行为金融学和行为心理学理论的角度进行解读和预测。
                {self_improve()}
                '''
            ),
            llm=haiku,
            max_iter=5,
            max_rpm=5,
            memory=True,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "行为金融分析师"),
        )

    technical_financial_analysis_agent = Agent(
            role="技术金融分析师",
            goal="基于金融数据或指标进行技术分析",
            tools=[financial_indicators_tool] + vision_tools.tools(),
            backstory=dedent(
                f"""
                你是最好的股票技术分析师。你从不关注行为分析或基本面分析，而是认为可以只通过技术分析做出预测。无论给你什么金融数据或指标，你都只会从技术分析的角度进行解读和预测。
                {self_improve()}
                """
            ),
            memory=True,
            llm=haiku,
            max_iter=5,
            max_rpm=5,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "技术金融分析师"),
        )

    best_financial_agent = Agent(
            role="最佳金融专家",
            goal="组织团队讨论并给出股票在下个月的操作和对应的置信度",
            backstory=dedent(
                f"""
                你是全世界最棒的金融专家，你对于股票趋势由着敏锐的嗅觉，你擅长组织和协调，并最终综合别人的观点。
                """
            ),
            verbose=True,
            memory=True,
            llm=gpt4o,
            max_iter=1,
            max_rpm=5,
            allow_delegation=True,
        )
        
    behavioral_financial_analysis_task = Task(
        description=dedent(
            f"""\
                与‘技术金融分析师’辩论，根据工具给定的{stock}股票金融数据和指标，仔细思考其中的行为金融原理/心理学原理，给出你对于这只股票在下个月（2024-6）的操作观点（持有，抛售还是购买），并给出对应的置信度和理由。
            """
        ),
        expected_output="提供“抛售”、“购买”和“持有”的建议以及信心水平和理由",
        # output_pydantic=Output,
        async_execution=False,
        agent=behavioral_financial_analysis_agent,
        output_file=f"./output/behavioral_financial_analysis_{time.time()}.md",
    )

    technical_financial_analysis_task = Task(
        description=dedent(
            f"""\
                与'行为金融分析师'辩论，根据工具给定的{stock}股票金融数据和指标，仔细思考其中的技术分析原理，给出你对于这只股票在下个月（2024-6）的操作观点（持有，抛售还是购买），并给出对应的置信度和理由。
            """
        ),
        expected_output="提供'抛售'、'购买'和'持有'的建议以及信心水平和理由",
        # output_pydantic=Output,
        async_execution=False,
        agent=technical_financial_analysis_agent,
        output_file=f"./output/technical_financial_analysis_{time.time()}.md",
    )

    best_financial_task = Task(
        description=dedent(
            f"""\
            指导行为金融分析师和技术金融分析师对于{stock}股票数据的辩论，辩论主题是：{stock}股票在下一个月是应该持有，抛售还是购买？
            总结前一个分析师的结果并告诉下一个分析师，让下一个分析师提供观点（赞同或反对），最后根据他们的辩论，给出当前股票在下个月的走势（持有，卖出或买入）以及信心水平。
            让他们重复读取相同的工具是没有意义的，而是让他们读一次之后，可以逐步根据数据缓存进行讨论，
            当他们观点达成一致的时候，你应该及时结束讨论并公布结果。
            """
        ),
        expected_output="提供最终的'抛售'，'购买'和'持有'的建议以及相应的信心水平和理由",
        # output_pydantic=Output,
        async_execution=True,
        agent=best_financial_agent,
        output_file=f"./output/best_financial_{time.time()}.md",
    )

    crew = Crew(
        agents=[behavioral_financial_analysis_agent, technical_financial_analysis_agent],
        tasks=[behavioral_financial_analysis_task, technical_financial_analysis_task, best_financial_task],
        process=Process.hierarchical,
        # manager_llm=llm,
        memory=False,
        manager_agent=best_financial_agent
    )

    return crew.kickoff()


if __name__ == '__main__':
    stock = "阿里巴巴"
    behavior_technical_group(stock)
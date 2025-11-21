import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_together import Together
from langchain_openai import ChatOpenAI
from textwrap import dedent
from scheduler.prompt_tips import self_improve, explain_why
from crewai import Agent
from scheduler.tools import (
    earningscall_tools,
    keyword_news_tools,
    public_headline_tools,
    search_tools,
    financial_data_tools,
    company_news_tools
)
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_HAIKU,
    CLAUDE_OPUS,
    GROQ_API_KEY,
    GROQ_MIXTRAL_8x7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B,
    TOGETHER_LLAMA3_70B,
    FIREWORKS_API_KEY,
    FIREWORKS_HERMES2PRO_MISTRAL_7B,
    GPT4O,
    OPENAI_API_KEY
)


llm = ChatAnthropic(
    model_name=CLAUDE_OPUS,
    api_key=CLAUDE_API_KEY, # type: ignore
    temperature=0.5,
)

llm_1 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_2 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_3 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_4 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_5 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_6 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

class FinancialAgents:
    def company_stock_news_analysis_agent(self):
        return Agent(
            role="Company Stock News Analyst",
            goal="To systematically gather and analyze news articles related to a specific company or stock, evaluating their sentiment, relevance, and potential impact on the company's market performance and reputation",
            tools=public_headline_tools.tools()
            + company_news_tools.tools()
            + keyword_news_tools.tools()
            + search_tools.tools(),
            backstory=dedent(
                f"""
                In the fast-paced world of financial markets, where information is king, you serve as the gatekeeper of news for a specific 
                company or stock. Your algorithmic eyes scan through endless streams of data and news, filtering out the noise to capture the 
                essence of how current events shape market perceptions and investor sentiments. Armed with advanced NLP tools, you dissect 
                the tone, context, and relevance of each piece of news, providing stakeholders with distilled insights that inform strategic 
                decisions.\n
                {self_improve()}
                """
            ),
            verbose=True,
            llm=llm_1,
            memory=True,
            max_iter=5,
            max_rpm=5,
            allow_delegation=False,
        )
    
    def earnings_call_analysis_agent(self):
        return Agent(
            role="Earnings Call Analyst",
            goal="To dissect and analyze earnings call transcripts of a specified company, extracting key financial data, strategic insights, and sentiment from executive discussions",
            tools=earningscall_tools.tools(),
            backstory=dedent(
                f"""\
                As an expert in corporate finance and strategic analysis, you delve into the nuances of earnings calls, where companies 
                unveil their performance and future directions. Armed with advanced NLP tools, you dissect these discussions, drawing out 
                the essence of executive commentary and financial disclosures. Your analysis illuminates the trajectory of the company, 
                shedding light on underlying trends, executive sentiment, and strategic moves.\n
                {self_improve()}
                """
            ),
            verbose=True,
            llm=llm_2,
            memory=True,
            max_iter=5,
            max_rpm=5,
            allow_delegation=False,
        )
    
    def financial_statements_agent(self):
        return Agent(
            role='Financial Statements Analyst',
            goal="To retrieve and analyze the Income Statement, Balance Sheet, Cash Flow Statement, Revenue, Quote Data of any specified company, providing a clear overview of the company's financial health.",
            backstory=f"""
                With an unparalleled command over financial analytics and a meticulous eye for detail, you delve into the financial 
                underpinnings of companies, big and small. Armed with the ability to swiftly access and decode financial statements, 
                you offer a lens through which the financial stability, operational efficiency, and growth prospects of any company 
                can be assessed.\n
                {self_improve()}
                """,
            tools=financial_data_tools.tools(),
            llm=llm_3,
            memory=True,
            max_iter=5,
            max_rpm=5,
            verbose=True,
            allow_delegation=False
        )

    def report_coordination_and_writing_agent(self):
        return Agent(
            role="Report coordination and writing Expert",
            goal="Compile all gathered information into a comprehensive and long-form document",
            backstory=dedent(
                f"""\
                    As a details-oriented senior editor at the Wall Street Journal known for your insightful and engaging articles,
                    your role is to consolidate research, analysis and strategic insights. A financial report should be as comprehensive 
                    and long-form as possible, and you need to build on the rest of the report by crafting an engaging and educational 
                    narrative that reveals new findings in an easy-to-understand way.\n
                    {self_improve()}
                """
            ),
            verbose=True,
            llm=llm_4,
            memory=True,
            max_iter=5,
            max_rpm=5,
            allow_delegation=True,
        )


from crewai import Crew, Process
from scheduler.tasks import FinancialTasks

tasks = FinancialTasks()
agents = FinancialAgents()

class Stock_Analysis_Team:
    def __init__(self, query):
        self.query = query
        self.agents = {}
        self.tasks = {}

    def __call__(self):
        self.create_agents_and_tasks()
        self.create_crew()
        result = self.crew.kickoff()
        metrics = self.crew.usage_metrics
        return result

    def create_agents_and_tasks(self):
        agent_types = [
            "company_stock_news_analysis",
            "financial_statements",
            "earnings_call_analysis",
            "report_coordination_and_writing",
        ]

        for agent_type in agent_types:
            agent_method = getattr(agents, f"{agent_type}_agent")
            task_method = getattr(tasks, f"{agent_type}_task")

            self.agents[agent_type] = agent_method()
            self.tasks[agent_type] = task_method(
                self.agents[agent_type], self.query)

        context_agent_types = [
            "company_stock_news_analysis",
            "earnings_call_analysis",
            "financial_statements",
        ]
        self.tasks["report_coordination_and_writing"].context = [
            self.tasks[agent_type] for agent_type in context_agent_types
        ]

    def create_crew(self):
        self.create_agents_and_tasks()
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=2,
            # memory=True,
            cache=True,
            full_output=True
        )


def run(query):
    parser = Stock_Analysis_Team(query=query)
    return parser()


if __name__ == "__main__":
    query = input('请输入您想分析的内容:')
    data = run(query=query)
    print("data:", data)